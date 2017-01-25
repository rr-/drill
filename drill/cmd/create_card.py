import argparse
from typing import List
import sqlalchemy as sa
from drill.cmd.command_base import CommandBase
from drill import db


PREPEND = 'prepend'
APPEND = 'append'


class CreateCardCommand(CommandBase):
    names = ['add-card', 'create-card']

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck', nargs='?')
        parser.add_argument('-q', '--question', required=True)
        parser.add_argument('-a', '--answer', required=True, nargs='+')
        parser.add_argument('-t', '--tag', nargs='*')
        parser.add_argument(
            '-p', '--place', choices=(PREPEND, APPEND), default=PREPEND)

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        question: str = args.question
        answers: List[str] = args.answer
        tags: List[str] = args.tag
        prepend: bool = args.place == PREPEND

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)

            max_card_num = db.get_max_card_num(session, deck)
            card = db.Card()
            card.num = max_card_num + 1
            card.question = question
            card.answers = answers
            card.tags = tags
            card.is_active = False
            card.due_date = None
            deck.cards.append(card)
            if prepend:
                max_active_card_num = session \
                    .query(sa.func.max(db.Card.num)) \
                    .filter(db.Card.deck_id == deck.id) \
                    .filter(db.Card.is_active == 1) \
                    .scalar()
                session \
                    .query(db.Card) \
                    .filter(db.Card.deck_id == deck.id) \
                    .filter(db.Card.is_active == 0) \
                    .update({'num': db.Card.num + 1})
                card.num = max_active_card_num + 1
