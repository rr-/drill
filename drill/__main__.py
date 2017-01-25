#!/usr/bin/env python3
import sys
import argparse
import errno
from drill import db, error
from drill.cmd import get_all_commands


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Study flashcards')
    subparsers = parser.add_subparsers(
        help='choose the command', dest='command')

    for command in get_all_commands():
        subparser = subparsers.add_parser(
            command.names[0], aliases=command.names[1:])
        command.decorate_arg_parser(subparser)

    args = parser.parse_args()
    if not args.command:
        parser.print_usage()
        sys.exit(1)
    return args


def main() -> None:
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
    db.init()
    main()
