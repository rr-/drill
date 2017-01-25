import argparse
from typing import Optional, List
from drill.cmd.command_base import CommandBase
from drill import db, util


class UpdateCardCommand(CommandBase):
    names = ['update-card']

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck')
        parser.add_argument('id', type=int)
        parser.add_argument('-q', '--question')
        parser.add_argument('-a', '--answer', nargs='+')
        parser.add_argument('-t', '--tag', nargs='*')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        num: int = args.id
        question: Optional[str] = args.question
        answers: Optional[List[str]] = args.answer
        tags: Optional[List[str]] = args.tag

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            card = db.get_card_by_num(session, deck, num)

            if not util.confirm(
                    'Are you sure you want to update card #%d (%r)?'
                    % (card.num, card.question)):
                return

            if question is not None:
                card.question = question

            if answers is not None:
                card.answers = answers

            if tags is not None:
                card.tags = tags
