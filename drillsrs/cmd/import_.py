import argparse
import json
import sys
import io
from typing import IO, Any, Optional

from dateutil.parser import parse as parse_date
from anki_export import ApkgReader
from lxml import etree

from drillsrs import db, scheduler, util
from drillsrs.cmd.command_base import CommandBase


def tojson(filepath):
    with ApkgReader(filepath) as apkg:
        temp = apkg.export()
    temp = temp[list(temp)[0]]
    x = {"name":temp[1][3], "description":None, "tags":[], "cards":[]}
    counter = 1
    for s in temp[1:]:
        card = {"active":False,"activation_date":None,"tags":[],"user_answers":[]}
        card["id"] = counter
        q = etree.HTML(s[0])
        card["question"] = etree.tostring(q, encoding='unicode', method='text')
        a = etree.HTML(s[1])
        card["answers"] = [" "] if a is None else [etree.tostring(a, encoding='unicode', method='text')]
        counter = counter + 1
        x["cards"].append(card)
    return(json.dumps(x))



def _import(handle: IO[Any]) -> None:
    with db.session_scope() as session:
        deck_obj = json.load(handle)

        deck = db.Deck()
        deck.name = deck_obj["name"]
        deck.description = deck_obj["description"]

        existing_deck = db.try_get_deck_by_name(session, deck.name)
        if existing_deck:
            if not util.confirm(
                "Are you sure you want to overwrite deck %r?" % deck.name
            ):
                return
            session.delete(existing_deck)
            session.commit()

        tag_dict = {}
        for tag_obj in deck_obj["tags"]:
            tag = db.Tag()
            tag.name = tag_obj["name"]
            tag.color = tag_obj["color"]
            deck.tags.append(tag)
            tag_dict[tag.name] = tag

        for card_obj in deck_obj["cards"]:
            card = db.Card()
            card.num = card_obj["id"]
            card.question = card_obj["question"]
            card.answers = card_obj["answers"]
            card.is_active = card_obj["active"]
            card.tags = [tag_dict[name] for name in card_obj["tags"]]
            for user_answer_obj in card_obj["user_answers"]:
                user_answer = db.UserAnswer()
                user_answer.date = parse_date(user_answer_obj["date"])
                user_answer.is_correct = user_answer_obj["correct"]
                card.user_answers.append(user_answer)
            if "activation_date" in card_obj:
                if card_obj["activation_date"]:
                    card.activation_date = parse_date(
                        card_obj["activation_date"]
                    )
            elif card.user_answers:
                card.activation_date = sorted(
                    card.user_answers, key=lambda ua: ua.date
                )[0].date
            card.due_date = scheduler.next_due_date(card)
            deck.cards.append(card)
        session.add(deck)


class ImportCommand(CommandBase):
    names = ["import"]
    description = "import a deck from a JSON file"

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "path",
            nargs="?",
            help="path to import from; if omitted, standard input is used",
        )
        parser.add_argument(
            "-a",
            action="store_true",
            help="Import Anki Deck",
        )

    def run(self, args: argparse.Namespace) -> None:
        path: Optional[str] = args.path
        anki = args.a
        if path:
            if anki:
                handle = io.StringIO(tojson(path))
                _import(handle)
            else:
                with open(path, "r") as handle:
                    _import(handle)
        else:
            _import(sys.stdin)
