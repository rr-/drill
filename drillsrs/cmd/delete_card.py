import argparse
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db, util


class DeleteCardCommand(CommandBase):
    names = ['delete-card']
    description = 'delete a single flashcard'

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            'deck', help='choose the deck to delete the card from')
        parser.add_argument('id', type=int, help='choose the card id')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        num: int = args.id
        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            card = db.get_card_by_num(session, deck, num)
            if not util.confirm(
                    'Are you sure you want to delete card #%d (%r)?'
                    % (card.num, card.question)):
                return
            for user_answer in card.user_answers:
                session.delete(user_answer)
            session.delete(card)
