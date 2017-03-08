import argparse
import sys
import json
from datetime import datetime
from typing import Optional, IO, Any
import sqlalchemy as sa
from drillsrs.cmd.command_base import CommandBase
from drillsrs import db


def _json_serializer(obj: object) -> object:
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError('Type not serializable')


def _export(deck: db.Deck, handle: IO[Any]) -> None:
    json.dump(
        {
            'name': deck.name,
            'description': deck.description,
            'tags':
            [{
                'name': tag.name,
                'color': tag.color,
            } for tag in deck.tags],
            'cards':
            [{
                'id': card.num,
                'question': card.question,
                'answers': card.answers,
                'active': card.is_active,
                'activation_date': card.activation_date,
                'tags': [tag.name for tag in card.tags],
                'user_answers':
                [{
                    'date': answer.date,
                    'correct': answer.is_correct,
                } for answer in card.user_answers],
            } for card in deck.cards],
        },
        handle,
        default=_json_serializer,
        separators=(',', ':'),
        check_circular=False)


class ExportCommand(CommandBase):
    names = ['export']
    description = 'export a deck to a JSON file'

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('deck', help='choose the deck to export')
        parser.add_argument(
            'path', nargs='?',
            help='path to export to; if omitted, standard output is used')

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        path: Optional[str] = args.path

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            deck = (
                session
                .query(db.Deck)
                .filter(db.Deck.id == deck.id)
                .options(
                    sa.orm
                    .subqueryload(db.Deck.cards)
                    .subqueryload(db.Card.tags),
                    sa.orm
                    .subqueryload(db.Deck.cards)
                    .subqueryload(db.Card.user_answers))
                .one())

            if path:
                with open(path, 'w') as handle:
                    _export(deck, handle)
            else:
                _export(deck, sys.stdout)
