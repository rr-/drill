import argparse
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db, util


class DeleteTagCommand(CommandBase):
    names = ['delete-tag']
    description = 'delete a tag from the deck'

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            'deck', help='choose the deck to delete the card from')
        parser.add_argument('tag', help='choose the tag name')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        tag_name: str = args.tag
        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            tag = db.get_tag_by_name(session, deck, tag_name)
            if not util.confirm(
                    'Are you sure you want to delete tag %r?' % tag.name):
                return
            session.delete(tag)
