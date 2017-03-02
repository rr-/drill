import argparse
from typing import List, TypeVar, Type


T = TypeVar('T', bound='CommandBase')


class CommandBase:
    names: List[str] = []
    description: str = ''
    registry: List['CommandBase'] = []

    def __init_subclass__(cls: Type[T]) -> None:
        cls.registry.append(cls())

    def decorate_arg_parser(self, _parser: argparse.ArgumentParser) -> None:
        pass

    def run(self, _args: argparse.Namespace) -> None:
        raise NotImplementedError()


def get_all_commands() -> List[CommandBase]:
    return CommandBase.registry
