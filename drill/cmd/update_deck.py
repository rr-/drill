import argparse
from typing import Optional
from drill.cmd.command_base import CommandBase
from drill import db


class UpdateDeckCommand(CommandBase):
    names = ['update-deck']

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck')
        parser.add_argument('--description')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        deck_description: Optional[str] = args.description

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            if deck_description is not None:
                deck.description = deck_description
