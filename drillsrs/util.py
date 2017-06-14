import os
import readline
from datetime import timedelta
from typing import List
from drillsrs import db


COLOR_SUCCESS = '\x1B[38;5;10m'
COLOR_FAIL = '\x1B[38;5;9m'
COLOR_RESET = '\x1B[0m'
COLOR_XTERM_TEMPLATE = '\x1B[38;5;%dm'
COLOR_TAGS = {
    'grey': COLOR_XTERM_TEMPLATE % 0x0F,
    'blue': COLOR_XTERM_TEMPLATE % 0x0C,
    'green': COLOR_XTERM_TEMPLATE % 0x0A,
    'red': COLOR_XTERM_TEMPLATE % 0x09,
    'aqua': COLOR_XTERM_TEMPLATE % 0x0E,
    'pink': COLOR_XTERM_TEMPLATE % 0x0D,
    'yellow': COLOR_XTERM_TEMPLATE % 0x0B,
}


def format_timedelta(delta: timedelta) -> str:
    seconds = abs(int(delta.total_seconds()))
    periods = [
        (60 * 60 * 24 * 365, 'year'),
        (60 * 60 * 24 * 30, 'month'),
        (60 * 60 * 24, 'day'),
        (60 * 60, 'hour'),
        (60, 'minute'),
        (1, 'second')
    ]

    parts = []
    for period_seconds, period_name in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            part = '%s %s' % (period_value, period_name)
            if period_value > 1:
                part += 's'
            parts.append(part)
    ret = ', '.join(parts)
    if delta.total_seconds() < 0:
        ret = '-' + ret
    return ret


def ask(text: str) -> str:
    return input(text)


def confirm(text: str) -> bool:
    while True:
        choice = input(text.strip(' ') + ' ').lower()
        if choice in ('yes', 'y', 'ye', 'yep', 'yeah'):
            return True
        elif choice in ('no', 'n', 'nah', 'nay'):
            return False
        else:
            print("Please respond with 'yes' or 'no'")


def color(text: str, color_str: str) -> str:
    return color_str + text + COLOR_RESET


def format_card_tag(tag: db.Tag) -> str:
    return color(tag.name, COLOR_TAGS.get(tag.color, COLOR_TAGS['grey']))


def format_card_tags(tags: List[db.Tag]) -> str:
    return ', '.join(format_card_tag(tag) for tag in tags)


def get_data(file_name: str) -> str:
    here = os.path.dirname(__file__)
    template_path = os.path.join(here, 'data', file_name)
    with open(template_path, 'r') as handle:
        return handle.read()
