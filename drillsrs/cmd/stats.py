import argparse
import sys
import json
from datetime import datetime, timedelta
from typing import Any, Tuple, Union, List
import sqlalchemy as sa
import jinja2
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db, util


class HistoryItem:
    def __init__(self,
            date: datetime,
            new_active_card_count: int,
            total_active_card_count: int,
            correct_answer_count: int,
            incorrect_answer_count: int):
        self.date = date
        self.new_active_card_count = new_active_card_count
        self.total_active_card_count = total_active_card_count
        self.correct_answer_count = correct_answer_count
        self.incorrect_answer_count = incorrect_answer_count


def _percent(count: Union[int, float], max_count: Union[int, float]) -> str:
    if not max_count:
        fraction = 100.0
    else:
        fraction = count * 100.0 / max_count
    return '%.02f' % fraction


def _to_json(input: Any) -> str:
    class DateEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            if type(obj) is HistoryItem:
                return {
                    'date': obj.date,
                    'new_active_card_count': obj.new_active_card_count,
                    'total_active_card_count': obj.total_active_card_count,
                    'correct_answer_count': obj.correct_answer_count,
                    'incorrect_answer_count': obj.incorrect_answer_count,
                }
            return json.JSONEncoder.default(self, obj)

    return json.dumps(input, cls=DateEncoder)

def _format_tags(tags: List[db.Tag]) -> str:
    return ', '.join(
        '<span class="tag-%s">%s</span>' % (tag.color, tag.name)
        for tag in tags)


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


def _get_learning_history(
        session: Any, deck: db.Deck) -> List[HistoryItem]:
    threshold = 365

    date_to_activated_card_count_map = {
        result[0].date(): result[1]
        for result in (
            session
            .query(db.Card.activation_date, sa.func.count(db.Card.id))
            .filter(db.Card.activation_date != None)
            .filter(db.Card.activation_date
                >= datetime.today() - timedelta(days=threshold))
            .group_by(sa.func.strftime('%Y-%m-%d', db.Card.activation_date))
            .all())}

    if date_to_activated_card_count_map:
        first_day = sorted(date_to_activated_card_count_map.keys())[0]
        threshold = min(
            threshold, (datetime.today().date() - first_day).days + 1)
    else:
        threshold = 1

    date_to_answer_count_map = {
        (result[0].date(), result[1]): result[2]
        for result in (
            session
            .query(
                db.UserAnswer.date,
                db.UserAnswer.is_correct,
                sa.func.count(db.UserAnswer.id))
            .filter(db.UserAnswer.date != None)
            .filter(db.UserAnswer.date
                >= datetime.today() - timedelta(days=threshold))
            .group_by(
                sa.func.strftime('%Y-%m-%d', db.UserAnswer.date),
                db.UserAnswer.is_correct)
            .all())}

    ret: List[HistoryItem] = []
    total_active_card_count = (
        session
        .query(sa.func.count(db.Card.id))
        .filter(db.Card.activation_date
            < datetime.today() - timedelta(days=threshold))
        .scalar())
    for delta in reversed(range(threshold)):
        date = datetime.today().date() - timedelta(days=delta)
        new_active_card_count = date_to_activated_card_count_map.get(date, 0)
        total_active_card_count += new_active_card_count
        ret.append(HistoryItem(
            date,
            new_active_card_count,
            total_active_card_count,
            date_to_answer_count_map.get((date, True), 0),
            date_to_answer_count_map.get((date, False), 0)))
    return ret


def _get_bad_cards(
        session: Any, deck: db.Deck, threshold: float) -> List[db.Card]:
    ratio = db.Card.correct_answer_count * 1.0 / db.Card.total_answer_count
    return list(
        session
        .query(db.Card)
        .filter(db.Deck.id == deck.id)
        .filter(ratio < threshold)
        .order_by(ratio.asc())
        .all())


def _write_report(deck: db.Deck, session: Any, output_handle: Any) -> None:
    template = jinja2.Template(util.get_data('stats.tpl'))
    template.globals['percent'] = _percent
    template.globals['tags'] = _format_tags
    template.globals['tojson'] = _to_json

    bad_cards_threshold = 0.75

    text = template.render(
        deck=deck,
        date=datetime.now(),
        learning_history=_get_learning_history(session, deck),
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
    description = 'produce an HTML report about the chosen deck'

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck', nargs='?', help='choose the deck name')
        parser.add_argument(
            'output', nargs='?',
            help='path to output to; if omitted, standard output is used')

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
