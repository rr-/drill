from datetime import datetime, timedelta
from typing import List, Optional, Any
from drillsrs import db


THRESHOLDS = [
    timedelta(seconds=0),
    timedelta(hours=4),
    timedelta(hours=8),
    timedelta(days=1),
    timedelta(days=3),
    timedelta(days=7),
    timedelta(days=14),
    timedelta(days=30),
    timedelta(days=120),
]


def consecutive_correct_answers(card: db.Card) -> int:
    for i, user_answer in enumerate(reversed(card.user_answers)):
        if not user_answer.is_correct:
            return i
    return len(card.user_answers)


def next_due_date(card: db.Card) -> Optional[datetime]:
    if not card.is_active:
        return None
    if not card.user_answers:
        return datetime.now()

    index = 0
    for user_answer in card.user_answers:
        if user_answer.is_correct:
            index = min(index + 1, len(THRESHOLDS) - 1)
        else:
            index = max(index - 1, 0)
    return card.user_answers[-1].date + THRESHOLDS[index]


def get_cards_to_study(
        session: Any, deck: db.Deck, how_many: int) -> List[db.Card]:
    return (
        session.query(db.Card)
        .filter(db.Card.deck_id == deck.id)
        .filter(db.Card.is_active == 0)
        .order_by(db.Card.num.asc())
        .limit(how_many))


def get_due_cards(session: Any, deck: db.Deck) -> List[db.Card]:
    return (
        session.query(db.Card)
        .filter(db.Card.deck_id == deck.id)
        .filter(db.Card.is_active)
        .order_by(db.Card.due_date.asc()))


def get_cards_to_review(session: Any, deck: db.Deck) -> List[db.Card]:
    return [
        card
        for card in get_due_cards(session, deck)
        if card.due_date and datetime.now() >= card.due_date]
