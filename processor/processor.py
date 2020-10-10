from typing import Dict, List, TYPE_CHECKING

from processor.capability import Capability
from processor.module import Module

if TYPE_CHECKING:
    from package import Package


class Processor:
    inconming: Dict[Capability, Module]
    outgoing: Dict[Capability, Module]

    def __init__(
        self,
        modules: List[Module],
    ):
        for module in modules:
            for inconming in module.incoming:
                if inconming not in self.inconming:
                    self.inconming[inconming] = module
                else:
                    raise Exception(f"Outgoing already exists: {inconming}")
            for outgoing in module.outgoing:
                if outgoing not in self.outgoing:
                    self.outgoing[outgoing] = module
                else:
                    raise Exception(f"Outgoing already exists: {outgoing}")

    def process(self, pkg: "Package"):
        self.inconming[pkg.type].process(pkg)
