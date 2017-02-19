import argparse
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Tuple, List
import sqlalchemy as sa
import jinja2
from drill.cmd.command_base import CommandBase
from drill import db


class AnswerHistogram(list):
    @property
    def length(self):
        return sum(item.weight for item in self)

    @property
    def max_value(self):
        return max(
            *[
                item.incorrect_answer_count + item.correct_answer_count
                for item in self
            ],
            1)


class AnswerHistogramItem:
    def __init__(
            self,
            correct_answer_count: int,
            incorrect_answer_count: int,
            weight: int) -> None:
        self.correct_answer_count = correct_answer_count
        self.incorrect_answer_count = incorrect_answer_count
        self.weight = weight

    @property
    def total_answer_count(self):
        return self.correct_answer_count + self.incorrect_answer_count


def _comparer(card: db.Card) -> Any:
    return card.incorrect_answer_count, -card.correct_answer_count


def _get_max_answer_count(session: Any, deck: db.Deck) -> int:
    tmp = sa.func.count(db.UserAnswer.id).label('cnt')
    return (
        session
        .query(tmp)
        .join(db.Card)
        .group_by(db.Card.id)
        .filter(db.Deck.id == deck.id)
        .order_by(tmp.desc())
        .limit(1)
        .scalar())


def _get_correct_answer_count(session: Any, deck: db.Deck) -> int:
    return (
        session
        .query(sa.func.count(db.UserAnswer.id))
        .join(db.Card)
        .filter(db.UserAnswer.is_correct == 1)
        .filter(db.Deck.id == deck.id)
        .scalar())


def _get_incorrect_answer_count(session: Any, deck: db.Deck) -> int:
    return (
        session
        .query(sa.func.count(db.UserAnswer.id))
        .join(db.Card)
        .filter(db.UserAnswer.is_correct == 0)
        .filter(db.Deck.id == deck.id)
        .scalar())


def _get_active_card_count(session: Any, deck: db.Deck) -> int:
    return (
        session
        .query(sa.func.count(db.Card.id))
        .filter(db.Card.is_active == 1)
        .filter(db.Deck.id == deck.id)
        .scalar())


def _get_inactive_card_count(session: Any, deck: db.Deck) -> int:
    return (
        session
        .query(sa.func.count(db.Card.id))
        .filter(db.Card.is_active == 0)
        .filter(db.Deck.id == deck.id)
        .scalar())


def _get_activity_histogram(session: Any, deck: db.Deck) -> List[int]:
    ret: List[int] = []
    for day in reversed(range(1, 365, 7)):
        date = datetime.today() - timedelta(days=day)
        ret.append(
            session
            .query(sa.func.count(db.Card.id))
            .filter(db.Card.first_answer_date < date)
            .filter(db.Deck.id == deck.id)
            .scalar())
    return ret


def _get_answer_histogram(session: Any, deck: db.Deck) -> AnswerHistogram:
    cards: Tuple[int, int] = (
        session
        .query(db.Card)
        .filter(db.Card.deck_id == deck.id)
        .filter(db.Card.is_active == 1)
        .order_by(db.Card.num.asc())
        .all())
    cards.sort(key=_comparer)
    ret = AnswerHistogram()
    last_item = None
    for card in cards:
        if last_item \
                and last_item.correct_answer_count == \
                card.correct_answer_count \
                and last_item.incorrect_answer_count == \
                card.incorrect_answer_count:
            last_item.weight += 1
        else:
            item = AnswerHistogramItem(
                correct_answer_count=card.correct_answer_count,
                incorrect_answer_count=card.incorrect_answer_count,
                weight=1)
            ret.append(item)
            last_item = item
    return ret


def _get_bad_cards(
        session: Any, deck: db.Deck, threshold: float) -> List[db.Card]:
    ratio = db.Card.correct_answer_count * 1.0 / db.Card.total_answer_count
    return (
        session
        .query(db.Card)
        .filter(db.Deck.id == deck.id)
        .filter(ratio < threshold)
        .order_by(ratio.asc())
        .all())


def _write_report(deck: db.Deck, session: Any, output_handle: Any) -> None:
    here = os.path.dirname(__file__)
    template_path = os.path.join(here, os.pardir, 'data', 'stats.tpl')
    with open(template_path, 'r') as handle:
        template = jinja2.Template(handle.read())

    activity_histogram = _get_activity_histogram(session, deck)
    answer_histogram = _get_answer_histogram(session, deck)
    bad_cards_threshold = 0.75

    text = template.render(
        deck=deck,
        answer_histogram=answer_histogram,
        activity_histogram=activity_histogram,
        activity_histogram_max=max(*activity_histogram, 1),
        bad_cards_threshold=bad_cards_threshold,
        bad_cards=_get_bad_cards(session, deck, bad_cards_threshold),
        max_answer_count=_get_max_answer_count(session, deck),
        active_card_count=_get_active_card_count(session, deck),
        inactive_card_count=_get_inactive_card_count(session, deck),
        correct_answer_count=_get_correct_answer_count(session, deck),
        incorrect_answer_count=_get_incorrect_answer_count(session, deck))
    print(text, file=output_handle)


class StatsCommand(CommandBase):
    names = ['stats']

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck', nargs='?')
        parser.add_argument('output', nargs='?', help='output file')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        path: str = args.output

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            if path:
                with open(path, 'w') as handle:
                    _write_report(deck, session, handle)
            else:
                _write_report(deck, session, sys.stdout)
