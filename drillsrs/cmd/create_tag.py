import argparse
from typing import Optional
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db


class CreateTagCommand(CommandBase):
    names = ['add-tag', 'create-tag']
    description = 'add a new tag to a deck'

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            'deck', nargs='?', help='choose the deck to add the card to')
        parser.add_argument(
            '-n', '--name', required=True, help='set the tag\'s name')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        tag_name: str = args.name

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)

            tag = db.Tag()
            tag.name = tag_name
            deck.tags.append(tag)
