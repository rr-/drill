#!/usr/bin/env python3
import sys
import argparse
import errno
from drillsrs import db, error
from drillsrs.cmd import get_all_commands


class CustomFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=80)

    def _format_action_invocation(self, action):
        if action.nargs == argparse.PARSER:
            return ''
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string

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


def parse_args() -> argparse.Namespace:
    description = 'Spaced repetition flashcard program for learning anything.'

    parser = argparse.ArgumentParser(
        description=description, formatter_class=CustomFormatter)
    subparsers = parser.add_subparsers(dest='command')

    for command in get_all_commands():
        subparser = subparsers.add_parser(
            command.names[0],
            aliases=command.names[1:],
            help=command.description,
            formatter_class=CustomFormatter)
        command.decorate_arg_parser(subparser)

    args = parser.parse_args()
    if not args.command:
        parser.print_usage()
        sys.exit(1)
    return args


def main() -> None:
    db.init()
    args = parse_args()
    try:
        for command in get_all_commands():
            if args.command in command.names:
                command.run(args)
                break
        else:
            assert False, 'Bad command'
    except IOError as ex:
        if ex.errno != errno.EPIPE:
            raise
    except (EOFError, KeyboardInterrupt, SystemExit):
        print()
        print('Interrupted.')
    except error.DrillError as ex:
        print(ex)


if __name__ == '__main__':
    main()
