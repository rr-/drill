import argparse
import random
from datetime import datetime

from drillsrs import db, scheduler, util
from drillsrs.cli_args import Mode
from drillsrs.cmd.command_base import CommandBase
from drillsrs.question import render_question_prompt


def _learn_single_card(
    index: int, num_cards_to_study: int, card: db.Card, mode: Mode
) -> None:
    print(
        "Card #{} ({:.01%} done, {} left)".format(
            card.num, index / num_cards_to_study, num_cards_to_study - index
        )
    )

    raw_question = card.question
    raw_answers = card.answers
    if mode is Mode.reversed or mode is Mode.mixed and random.random() > 0.5:
        raw_question, raw_answers = random.choice(raw_answers), [raw_question]

    util.ask(render_question_prompt(raw_question, raw_answers, card.tags))
    util.ask("Answers: %s" % ", ".join(raw_answers))
    print("")

    card.is_active = True
    card.due_date = scheduler.next_due_date(card)
    card.activation_date = datetime.now()


class StudyCommand(CommandBase):
    names = ["study", "learn"]
    description = "begin a study session"

    def decorate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("deck", nargs="?", help="choose the deck name")
        parser.add_argument(
            "-n", type=int, default=10, help="set how many flashcards to study"
        )
        parser.add_argument(
            "-m",
            "--mode",
            type=Mode.parse,
            default=Mode.direct,
            choices=list(Mode),
            help="learning mode. whether to involve reversed direction",
        )

    def run(self, args: argparse.Namespace) -> None:
        deck_name: str = args.deck
        how_many: int = args.n
        mode: Mode = args.mode

        with db.session_scope() as session:
            deck = db.get_deck_by_name(session, deck_name)
            cards_to_study = scheduler.get_cards_to_study(
                session, deck, how_many
            )

            if not cards_to_study:
                print("No cards to study.")
                return

            print(
                "%d cards to study. After seeing a card, hit enter."
                % len(cards_to_study)
            )
            print()

            num_cards_to_study = len(cards_to_study)
            for index, card in enumerate(cards_to_study):
                _learn_single_card(index, num_cards_to_study, card, mode)
