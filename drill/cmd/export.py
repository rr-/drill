import argparse
import sys
import json
from datetime import datetime
from typing import Optional, IO, Any
import sqlalchemy as sa
from drill.cmd.command_base import CommandBase
from drill import db


def _json_serializer(obj: object) -> object:
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError('Type not serializable')


def _export(handle: IO[Any]) -> None:
    with db.session_scope() as session:
        decks = (
            session
            .query(db.Deck)
            .options(
                sa.orm
                    .joinedload(db.Deck.cards)
                    .subqueryload(db.Card.user_answers)))

        json.dump(
            [{
                'name': deck.name,
                'description': deck.description,
                'cards':
                [{
                    'id': card.num,
                    'question': card.question,
                    'answers': card.answers,
                    'active': card.is_active,
                    'tags': card.tags,
                    'user_answers':
                    [{
                        'date': answer.date,
                        'correct': answer.is_correct,
                    } for answer in card.user_answers],
                } for card in deck.cards],
            } for deck in decks],
            handle,
            default=_json_serializer,
            separators=(',', ':'),
            check_circular=False)


class ExportCommand(CommandBase):
    names = ['export']

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('path', nargs='?')

    def run(self, args: argparse.Namespace) -> None:
        path: Optional[str] = args.path
        if path:
            with open(path, 'w') as handle:
                _export(handle)
        else:
            _export(sys.stdout)
