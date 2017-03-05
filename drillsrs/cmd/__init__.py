from drillsrs.cmd.command_base import CommandBase
from drillsrs.cmd.command_base import get_all_commands

from drillsrs.cmd.howto import HowToCommand

from drillsrs.cmd.list_decks import ListDecksCommand
from drillsrs.cmd.create_deck import CreateDeckCommand
from drillsrs.cmd.update_deck import UpdateDeckCommand
from drillsrs.cmd.delete_deck import DeleteDeckCommand

from drillsrs.cmd.list_tags import ListTagsCommand
from drillsrs.cmd.create_tag import CreateTagCommand
from drillsrs.cmd.update_tag import UpdateTagCommand
from drillsrs.cmd.delete_tag import DeleteTagCommand

from drillsrs.cmd.list_cards import ListCardsCommand
from drillsrs.cmd.create_card import CreateCardCommand
from drillsrs.cmd.update_card import UpdateCardCommand
from drillsrs.cmd.delete_card import DeleteCardCommand

from drillsrs.cmd.study import StudyCommand
from drillsrs.cmd.review import ReviewCommand
from drillsrs.cmd.stats import StatsCommand

from drillsrs.cmd.export import ExportCommand
__import__('drillsrs.cmd.import', globals(), locals(), ['ImportCommand'])
