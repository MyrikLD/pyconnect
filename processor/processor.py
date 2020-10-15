from typing import Callable, Dict, List, TYPE_CHECKING

from package.client import ClientConnection
from processor.capability import Capability
from processor.module import Module

if TYPE_CHECKING:
    from package import Package


class Processor:
    inconming: Dict[Capability, Module]
    outgoing: Dict[Capability, Module]
    write: Callable

    def __init__(
        self,
        modules: List[Module],
    ):
        self.inconming = {}
        self.outgoing = {}

        for module in modules:
            if hasattr(module, "incoming"):
                for inconming in module.incoming:
                    if inconming not in self.inconming:
                        self.inconming[inconming] = module
                    else:
                        raise Exception(f"Outgoing already exists: {inconming}")

            if hasattr(module, "outgoing"):
                for outgoing in module.outgoing:
                    if outgoing not in self.outgoing:
                        self.outgoing[outgoing] = module
                    else:
                        raise Exception(f"Outgoing already exists: {outgoing}")

    def process(self, client: "ClientConnection", pkg: "Package"):
        self.inconming[pkg.type].process(client, pkg)

    def set_writer(self, writer: Callable):
        self.write = writer
