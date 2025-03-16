from dataclasses import dataclass, field
from typing import Optional

@dataclass(eq=False, slots=True)
class Product:
    id: int
    name: str
    price: float
    category_id: int
    store_id: int
    seo_code: str
    brand: Optional[str] = field(default=None)
    manufacturer: Optional[str] = field(default=None)

    def __eq__(self, other) -> bool:
        if isinstance(other, Product):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(frozen=True, slots=True)
class StoreProduct:
    store_id: int
    product_id: int


@dataclass(frozen=True, slots=True)
class RequestStatus:
    status: str
    url: str


@dataclass(frozen=True, slots=True)
class DetailedRequestStatus(RequestStatus):
    category_id: int
    store_id: int
    offset: int