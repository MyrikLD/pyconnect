from collections import Callable
from logging import getLogger
from typing import Dict, TYPE_CHECKING

from .capability import Capability

if TYPE_CHECKING:
    from package import Client, Package


class Module:
    def __init__(self):
        self.log = getLogger(self.__class__.__name__)

    def process(self, client: "Client", pkg: "Package"):
        if pkg.type in self.incoming:
            self.incoming[pkg.type](self, client, pkg)
        else:
            raise Exception(
                f"No such capability in module {self.__class__.__name__}: {pkg.type}"
            )

    incoming: Dict[Capability, Callable]
    outgoing: Dict[Capability, Callable]
