import argparse
from drill.cmd.command_base import CommandBase
from drill import db, error


class CreateDeckCommand(CommandBase):
    names = ['create-deck']

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck')
        parser.add_argument('--description')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        deck_description: str = args.description
        with db.session_scope() as session:
            if db.try_get_deck_by_name(session, deck_name):
                raise error.DeckAlreadyExistsError(
                    'A deck with name %r already exists' % deck_name)
            deck = db.Deck()
            deck.name = deck_name
            deck.description = deck_description
            session.add(deck)
