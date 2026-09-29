import logging
from collections.abc import Iterator
from typing import Any, Generic, TypeVar, cast, overload

from sapwright.exceptions import SAPElementTypeMismatch
from sapwright.objects.component import ComponentT, GuiComponent

_InitT = TypeVar("_InitT", bound=GuiComponent)

logger = logging.getLogger(__name__)


def get_com_collection_item(com_collection: Any, index: int) -> Any:
    """Returns the COM object at the given index in the collection."""
    try:
        return com_collection.Item(index)
    except Exception:
        element_at = getattr(com_collection, "ElementAt", None)
        if element_at is not None:
            try:
                return element_at(index)
            except Exception as e:
                logger.debug(
                    f"Item(index) and ElementAt(index) failed: {e}, falling back to direct index access"
                )
        try:
            return com_collection(index)  # default member: collection(index)
        except Exception as e:
            logger.error(f"Failed to get element at index {index}: {e}")
        raise


class GuiComponentCollection(Generic[ComponentT]):
    """The GuiComponentCollection is used for collections elements such as the Children property of containers. Each element of the collection is an extension of GuiComponent."""

    @overload
    def __init__(
        self: "GuiComponentCollection[GuiComponent]",
        com_collection: Any,
        expected_type: None = None,
    ) -> None: ...

    @overload
    def __init__(
        self: "GuiComponentCollection[_InitT]",
        com_collection: Any,
        expected_type: type[_InitT],
    ) -> None: ...

    def __init__(
        self,
        com_collection: Any,
        expected_type: type[ComponentT] | None = None,
    ) -> None:

        self._com = com_collection
        self._expected_type = expected_type

    def __len__(self):
        return int(self._com.Count)

    def __getitem__(self, index: int) -> ComponentT:
        length = self._com.Count
        if index < 0:
            index += length

        if index < 0 or index >= length:
            raise IndexError(
                f"Index {index} out of range for collection of length {length}"
            )

        element = get_com_collection_item(self._com, index)

        expected_type = self._expected_type
        if expected_type is None:
            return cast(ComponentT, GuiComponent(element))

        if not expected_type.matches(element):
            raise SAPElementTypeMismatch(
                f"Element at index {index} is of type {element.Type}, expected {expected_type.__name__}"
            )

        return expected_type(element)

    def __iter__(self) -> Iterator[ComponentT]:
        """Iterate over all wrapped components."""
        for i in range(self._com.Count):
            yield self[i]
