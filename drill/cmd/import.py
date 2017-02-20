import argparse
import sys
import json
from typing import Optional, IO, Any
from dateutil.parser import parse as parse_date
from drill.cmd.command_base import CommandBase
from drill import db, scheduler


def _import(handle: IO[Any]) -> None:
    with db.session_scope() as session:
        session.query(db.Deck).delete()
        session.query(db.Card).delete()
        session.query(db.UserAnswer).delete()
        session.flush()

        for deck_obj in json.load(handle):
            deck = db.Deck()
            deck.name = deck_obj['name']
            deck.description = deck_obj['description']
            for card_obj in deck_obj['cards']:
                card = db.Card()
                card.num = card_obj['id']
                card.question = card_obj['question']
                card.answers = card_obj['answers']
                card.is_active = card_obj['active']
                card.tags = card_obj.get('tags', [])
                for user_answer_obj in card_obj['user_answers']:
                    user_answer = db.UserAnswer()
                    user_answer.date = parse_date(user_answer_obj['date'])
                    user_answer.is_correct = user_answer_obj['correct']
                    card.user_answers.append(user_answer)
                card.due_date = scheduler.next_due_date(card)
                deck.cards.append(card)
            session.add(deck)


class ImportCommand(CommandBase):
    names = ['import']

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('path', nargs='?')

    def run(self, args: argparse.Namespace) -> None:
        path: Optional[str] = args.path
        if path:
            with open(path, 'r') as handle:
                _import(handle)
        else:
            _import(sys.stdin)
