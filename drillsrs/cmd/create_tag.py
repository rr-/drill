import argparse
from typing import Optional
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db, util


class CreateTagCommand(CommandBase):
    names = ['add-tag', 'create-tag']
    description = 'add a new tag to a deck'

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            'deck', nargs='?', help='choose the deck to add the card to')
        parser.add_argument(
            '-n', '--name', required=True, help='set the tag\'s name')
        parser.add_argument(
            '-c', '--color', required=False, choices=util.COLOR_TAGS.keys(),
            help='set the tag\'s color')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        tag_name: str = args.name
        tag_color: Optional[str] = args.color

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)

            tag = db.Tag()
            tag.name = tag_name
            tag.color = tag_color
            deck.tags.append(tag)
