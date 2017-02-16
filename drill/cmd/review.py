import argparse
import random
from datetime import datetime
from typing import Any, List
from drill.cmd.command_base import CommandBase
from drill import db, scheduler, util


def _review_single_card(
        index: int, cards_to_review: List[db.Card], card: db.Card) -> None:
    print(
        'Card #%d (%d/%d, %d left)' % (
            card.num,
            index + 1,
            len(cards_to_review),
            len(cards_to_review) - index))

    print('Question: %s' % card.question, end='')
    if card.tags:
        print(' [%s]' % util.format_card_tags(card.tags), end='')
    print()

    while True:
        answer_text = util.ask('Answer: ')
        if answer_text:
            break

    if answer_text.lower() in [a.lower() for a in card.answers]:
        is_correct = True
        print(util.color('Correct!', util.COLOR_SUCCESS))
    else:
        print(util.color('Not quite...', util.COLOR_FAIL), end=' ')
        print('expected: ' + ', '.join(card.answers))
        print('0 - not correct')
        print('1 - correct, don\'t add alias')
        print('2 - correct, add alias')
        while True:
            try:
                choice = int(util.ask('Choice: '))
                assert choice in [0, 1, 2]
                break
            except ValueError:
                continue

        if choice == 0:
            is_correct = False
        elif choice == 1:
            is_correct = True
        elif choice == 2:
            is_correct = True
            card.answers.append(answer_text)
        else:
            assert False

    print()
    user_answer = db.UserAnswer()
    user_answer.date = datetime.now()
    user_answer.text = answer_text
    user_answer.is_correct = is_correct
    card.user_answers.append(user_answer)
    card.due_date = scheduler.next_due_date(card)


def _review(session: Any, deck: db.Deck) -> None:
    first_iteration = True
    while True:
        cards_to_review = scheduler.get_cards_to_review(session, deck)
        random.shuffle(cards_to_review)

        if not cards_to_review:
            due_cards = scheduler.get_due_cards(session, deck)

            if first_iteration:
                print('No cards to review.')
            else:
                print('No more cards to review.')
            if due_cards:
                next_due_date = due_cards[0].due_date
                assert next_due_date
                print('Next review in %s.' % util.format_timedelta(
                    next_due_date - datetime.now()))
            return

        if not first_iteration:
            print('%d cards to review.' % len(cards_to_review))
            print()

        for i, card in enumerate(cards_to_review):
            _review_single_card(i, cards_to_review, card)
            session.commit()

        first_iteration = False


class ReviewCommand(CommandBase):
    names = ['review']

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck', nargs='?')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            _review(session, deck)
