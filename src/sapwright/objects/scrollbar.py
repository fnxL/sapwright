from typing import Any


class GuiScrollbar:
    def __init__(self, com_scrollbar: Any):
        self._com = com_scrollbar

    @property
    def maximum(self) -> int:
        return int(self._com.Maximum)

    @property
    def minimum(self) -> int:
        return int(self._com.Minimum)

    @property
    def page_size(self) -> int:
        return int(self._com.PageSize)

    @property
    def position(self) -> int:
        return int(self._com.Position)

    @position.setter
    def position(self, value: int):
        self._com.Position = value

    @property
    def range(self) -> int:
        return int(self._com.Range)

    # Aliases
    Maximum = maximum
    Minimum = minimum
    PageSize = page_size
    Position = position
    Range = range
