import argparse
from typing import Optional, List
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db, util


class UpdateCardCommand(CommandBase):
    names = ['edit-card', 'update-card']
    description = 'edit a single flashcard'

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck', help='choose the deck of the card')
        parser.add_argument('id', type=int, help='choose the card id')
        parser.add_argument(
            '-q', '--question', help='set the card\'s question text')
        parser.add_argument(
            '-a', '--answer', nargs='+', help='set the card\'s answers text')
        parser.add_argument(
            '-t', '--tag', nargs='*', help='set the tags of the card')
        parser.add_argument(
            '--new-id', type=int,
            help='move the card to desired place in the deck')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        num: int = args.id
        question: Optional[str] = args.question
        answers: Optional[List[str]] = args.answer
        tags: Optional[List[str]] = args.tag
        new_num: Optional[int] = args.new_id

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
                card.tags = [
                    db.get_tag_by_name(session, deck, tag)
                    for tag in tags]

            if new_num is not None:
                db.move_card(session, card, new_num)
