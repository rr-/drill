import argparse
from typing import Any
import sqlalchemy as sa
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db, util


def _print_single_tag(session: Any, index: int, tag: db.Tag) -> None:
    tag_usages = (
        session
        .query(sa.func.count(db.CardTag.tag_id))
        .filter(db.CardTag.tag_id == tag.id)
        .scalar()) or 0
    print('Tag #%d' % (index + 1))
    print('Name:    %s' % tag.name)
    print('Color:   %s' % tag.color)
    print('Preview: [%s]' % util.format_card_tag(tag))
    print('Usages:  %d' % tag_usages)
    print()


class ListTagsCommand(CommandBase):
    names = ['list-tags']
    description = 'print all tags in a deck'

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck', nargs='?', help='choose the deck name')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            tags = (
                session
                .query(db.Tag)
                .filter(db.Tag.deck_id == deck.id)
                .all())

            if not tags:
                print('No tags to show.')
                return

            for i, tag in enumerate(tags):
                _print_single_tag(session, i, tag)
