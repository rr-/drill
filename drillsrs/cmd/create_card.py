import argparse
from typing import List
import sqlalchemy as sa
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db


PREPEND = 'prepend'
APPEND = 'append'


class CreateCardCommand(CommandBase):
    names = ['add-card', 'create-card']
    description = 'add a new flashcard to a deck'

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            'deck', nargs='?', help='choose the deck to add the card to')
        parser.add_argument(
            '-q', '--question', required=True,
            help='set the card\'s question text')
        parser.add_argument(
            '-a', '--answer', required=True, nargs='+',
            help='set the card\'s answers text')
        parser.add_argument(
            '-t', '--tag', nargs='*', help='add optional tags to the card')
        parser.add_argument(
            '-p', '--place', choices=(PREPEND, APPEND), default=PREPEND,
            help='choose where to put the card in the deck')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        question: str = args.question
        answers: List[str] = args.answer
        tags: List[str] = args.tag or []
        prepend: bool = args.place == PREPEND

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)

            max_card_num = db.get_max_card_num(session, deck)
            card = db.Card()
            card.num = max_card_num + 1
            card.question = question
            card.answers = answers
            card.tags = [
                db.get_tag_by_name(session, deck, tag)
                for tag in tags]
            card.is_active = False
            card.due_date = None
            deck.cards.append(card)
            if prepend:
                max_active_card_num = db.get_max_active_card_num(session, deck)
                db.move_card(session, card, max_active_card_num + 1)
