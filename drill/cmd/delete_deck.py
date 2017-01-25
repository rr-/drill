import argparse
from drill.cmd.command_base import CommandBase
from drill import db, util


class DeleteDeckCommand(CommandBase):
    names = ['delete-deck']

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            if not util.confirm(
                    'Are you sure you want to delete deck %r?' % deck_name):
                return
            session.delete(deck)
