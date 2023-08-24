from typing import List

from data.screen import AScreen
from logging import Logger
from logger import get_logger

logger: Logger = get_logger()


ROTATOR_DEFAULT_DELAY: int = 15


class Rotator:
    def __init__(self, id: str, delay: int, screens: List[AScreen]):
        self.__id: str = id
        self.__delay: int = delay
        self.__screens: List[AScreen] = screens

    @property
    def id(self) -> str:
        return self.__id

    @property
    def delay(self) -> int:
        return self.__delay

    @property
    def screens(self) -> List[AScreen]:
        return self.__screens
