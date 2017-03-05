import argparse
from typing import Optional
from datetime import datetime
from math import log10, ceil
import sqlalchemy as sa
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db, util


SORT_NONE = 'none'
SORT_DUE_DATE = 'due-date'


def _print_single_card(
        index_length: int, card: db.Card, show_answers: bool) -> None:
    print('Card %*s: ' % (index_length, '#%s' % card.num), end='')
    if card.is_active:
        correct_user_answers = [
            ua for ua in card.user_answers if ua.is_correct]

        due_date = card.due_date
        assert due_date

        print(
            '(answered %d time(s), %6.02f%% correct, due %s)' % (
                len(card.user_answers),
                len(correct_user_answers) * 100.0 / len(card.user_answers)
                if card.user_answers
                else 100,
                util.format_timedelta(due_date - datetime.now())),
            end=' ')
    print(card.question, end='')
    if show_answers:
        print(': %s' % ', '.join(card.answers), end='')
    if card.tags:
        print(' [%s]' % util.format_card_tags(card.tags), end='')
    print()


class ListCardsCommand(CommandBase):
    names = ['list-cards']
    description = 'print all flashcards in a deck'

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck', nargs='?', help='choose the deck name')
        parser.add_argument('-q', '--question', help='filter by question text')
        parser.add_argument('-t', '--tag', help='filter by tag')
        parser.add_argument(
            '--sort', default=SORT_NONE, choices=(SORT_NONE, SORT_DUE_DATE),
            help='change sort style')
        parser.add_argument(
            '--show-answers', action='store_true', help='show answers text')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        question: Optional[str] = args.question
        tag: Optional[str] = args.tag
        sort_style: str = args.sort
        show_answers: bool = args.show_answers

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            cards = session \
                .query(db.Card) \
                .filter(db.Card.deck_id == deck.id) \
                .options(sa.orm.subqueryload('user_answers'))

            if question is not None:
                cards = cards.filter(
                    sa.func.lower(db.Card.question).like(
                        sa.func.lower(question)))

            if sort_style == SORT_NONE:
                cards = cards.order_by(db.Card.num.asc())
            elif sort_style == SORT_DUE_DATE:
                cards = cards.order_by(db.Card.is_active.desc())
                cards = cards.order_by(db.Card.due_date.asc())
                cards = cards.order_by(db.Card.num.asc())
            else:
                assert False

            cards = cards.all()
            if tag is not None:
                cards = [
                    card
                    for card in cards
                    if tag.lower() in [t.name.lower() for t in card.tags]]

            if not cards:
                print('No cards to show.')
                return

            index_length = ceil(log10(db.get_max_card_num(session, deck)))
            for card in cards:
                _print_single_card(index_length, card, show_answers)
