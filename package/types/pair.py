from typing import Optional

from pydantic import BaseModel, Field


class Pair(BaseModel):
    pair: bool = True
    public_key: Optional[str] = Field(alias="publicKey")

    def dict(self, **kwargs):
        kwargs["exclude_unset"] = True
        kwargs["by_alias"] = True
        return super().dict(**kwargs)
