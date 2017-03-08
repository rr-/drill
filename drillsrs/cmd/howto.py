import argparse
import shutil
from textwrap import wrap
from drillsrs.cmd.command_base import CommandBase
from drillsrs import util


class HowToCommand(CommandBase):
    names = ['how-to']
    description = 'show a mini-tutorial how to use'

    def run(self, _args: argparse.Namespace) -> None:
        text = util.get_data('howto.txt')

        width, _height = shutil.get_terminal_size((80, 20))

        body = '\n'.join([
            '\n'.join(
                wrap(
                    line,
                    width=width,
                    break_long_words=False,
                    replace_whitespace=False))
            for line in text.splitlines()
        ])

        print(body)
