import argparse
from drill.cmd.command_base import CommandBase
from drill import db, scheduler, util


def _print_single_card(card: db.Card) -> None:
    print('Card #%d' % card.num)
    print('Question: %s' % card.question, end='')
    if card.tags:
        print(' [%s]' % util.format_card_tags(card.tags), end='')
    print()
    print('Answers: %s' % ', '.join(card.answers))


class StudyCommand(CommandBase):
    names = ['study', 'learn']

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck', nargs='?')
        parser.add_argument('-n', type=int, default=10)

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        how_many: int = args.n

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            cards_to_study = scheduler.get_cards_to_study(
                session, deck, how_many)

            if not cards_to_study:
                print('No cards to study.')
                return

            print(
                '%d cards to study. After seeing a card, hit enter.' %
                cards_to_study.count())
            print()

            for card in cards_to_study:
                _print_single_card(card)
                input('')
                card.is_active = True
                card.due_date = scheduler.next_due_date(card)
