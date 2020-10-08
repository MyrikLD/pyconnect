from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return self.value

    def __repr__(self):
        return f"{str(self)!r}"
