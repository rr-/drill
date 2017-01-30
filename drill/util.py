from datetime import timedelta
from typing import List


COLOR_SUCCESS = '\x1B[48;5;193m'
COLOR_FAIL = '\x1B[48;5;217m'
COLOR_RESET = '\x1B[0m'
COLOR_TAGS = [
    '\x1B[48;5;%dm' % num for num in [0xE6, 0xC2, 0xC3, 0xBD, 0xE1, 0xE0]]


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


def get_tag_color(tag: str) -> int:
    return sum(ord(c) for c in tag) % len(COLOR_TAGS)


def format_card_tags(tags: List[str]) -> str:
    ret = []
    for tag in tags:
        tag_num = get_tag_color(tag)
        ret.append(color(tag, COLOR_TAGS[tag_num]))
    return ', '.join(ret)
