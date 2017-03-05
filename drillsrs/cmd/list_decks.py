import argparse
import sqlalchemy as sa
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db


class ListDecksCommand(CommandBase):
    names = ['list-decks']
    description = 'print all decks'

    def run(self, _args: argparse.Namespace) -> None:
        with db.session_scope() as session:
            if not session.query(db.Deck).count():
                print('No decks to show.')
                return

            results = session.query(
                db.Deck.id, db.Deck.name, db.Deck.description)
            for deck_id, name, description in results:
                card_count = session \
                    .query(sa.func.count(db.Deck.cards)) \
                    .filter(db.Deck.id == deck_id) \
                    .scalar()
                print('%s: %s (%d cards)' % (
                    name, description or '(no description)', card_count))
