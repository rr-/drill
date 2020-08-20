import argparse
from typing import List, Type, TypeVar

T = TypeVar("T", bound="CommandBase")


class CommandBase:
    names: List[str] = []
    description: str = ""

    def decorate_arg_parser(self, _parser: argparse.ArgumentParser) -> None:
        pass

    def run(self, _args: argparse.Namespace) -> None:
        raise NotImplementedError()
