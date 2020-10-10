from collections import Callable
from typing import Dict, TYPE_CHECKING

from .capability import Capability

if TYPE_CHECKING:
    from package import Package


class Module:
    def process(self, pkg: "Package"):
        if pkg.type in self.incoming:
            self.incoming[pkg.type](pkg.message)
        else:
            raise Exception(
                f"No such capability in module {self.__class__.__name__}: {pkg.type}"
            )

    incoming: Dict[Capability, Callable]
    outgoing: Dict[Capability, Callable]
