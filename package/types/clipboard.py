from pydantic import BaseModel


class Clipboard(BaseModel):
    content: str

    def dict(self, **kwargs):
        kwargs["exclude_unset"] = True
        kwargs["by_alias"] = True
        return super().dict(**kwargs)


class ClipboardConnect(BaseModel):
    timestamp: int = 0

    def dict(self, **kwargs):
        kwargs["exclude_unset"] = True
        kwargs["by_alias"] = True
        return super().dict(**kwargs)
