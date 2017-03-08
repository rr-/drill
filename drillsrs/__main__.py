#!/usr/bin/env python3
import sys
import argparse
import errno
from typing import List
from drillsrs import cmd, db, error


class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=80)

    def _format_action_invocation(self, action):
        if action.nargs == argparse.PARSER:
            return ''
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        return '%s %s' % (
            ', '.join(action.option_strings),
            self._format_args(
                action, self._get_default_metavar_for_optional(action)))

    def _metavar_formatter(self, action, default_metavar):
        if action.metavar is not None:
            result = action.metavar
        elif action.choices is not None:
            choice_strs = [str(choice) for choice in action.choices]
            result = '{%s}' % ', '.join(choice_strs)
        else:
            result = default_metavar

        def fmt(tuple_size):
            if isinstance(result, tuple):
                return result
            return (result, ) * tuple_size

        return fmt


def create_arg_parser(
        commands: List[cmd.CommandBase],
        description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=description, formatter_class=CustomHelpFormatter)
    subparsers = parser.add_subparsers(dest='command')

    for command in commands:
        subparser = subparsers.add_parser(
            command.names[0],
            aliases=command.names[1:],
            help=command.description,
            formatter_class=CustomHelpFormatter)
        subparser.set_defaults(command_cls=command)
        command.decorate_arg_parser(subparser)

    return parser


def parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    args = parser.parse_args()
    if not args.command:
        parser.print_usage()
        sys.exit(1)
    return args


def execute_command_with_args(
        command: cmd.CommandBase, args: argparse.Namespace) -> None:
    try:
        command.run(args)
    except IOError as ex:
        if ex.errno != errno.EPIPE:
            raise
    except (EOFError, KeyboardInterrupt, SystemExit):
        print()
        print('Interrupted.')
    except error.DrillError as ex:
        print(ex)


def main() -> None:
    db.init()
    commands = cmd.get_all_commands()
    parser = create_arg_parser(
        commands,
        'Spaced repetition flashcard program for learning anything.')
    args = parse_args(parser)
    execute_command_with_args(args.command_cls, args)


if __name__ == '__main__':
    main()
