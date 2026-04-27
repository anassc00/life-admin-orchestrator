from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Any


class UnitOfWork(ABC, AbstractContextManager):  # type: ignore[type-arg]

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
