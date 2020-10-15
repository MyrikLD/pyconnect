from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Notification(BaseModel):
    payload_hash: Optional[str] = Field(alias="payloadHash")
    id: str
    only_once: Optional[bool] = Field(alias="onlyOnce")

    is_clearable: Optional[bool] = Field(alias="isClearable")
    is_cancel: Optional[bool] = Field(alias="isCancel")

    appName: Optional[str]
    time: Optional[int]
    ticker: Optional[str]
    title: Optional[str]
    text: Optional[str]

    actions: Optional[List[str]]
    request_reply_id: Optional[UUID] = Field(alias="requestReplyId")

    def __repr_args__(self):
        return self.dict(exclude_unset=True).items()

    def dict(self, **kwargs):
        kwargs["exclude_unset"] = True
        kwargs["by_alias"] = True
        return super().dict(**kwargs)
