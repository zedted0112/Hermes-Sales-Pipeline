"""Memory store — short-term session context and long-term recall hooks."""


class MemoryStore:
    def __init__(self) -> None:
        self._session: dict[str, object] = {}

    def set(self, key: str, value: object) -> None:
        self._session[key] = value

    def get(self, key: str, default: object = None) -> object:
        return self._session.get(key, default)
