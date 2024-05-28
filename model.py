from typing import Optional, Set
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)  # OrderLine 은 동작이 없는 불변 데이터 클래스다.
class OrderLine:
    orderid: str  # 주문 번호
    sku: str  # 제품 식별자
    qty: int  # 주문 수량


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref  # Batch 참조 번호
        self.sku = sku  # 제품 식별자
        self.eta = eta  # 예상 도착일
        self._purchased_quantity = qty  # 구매 수량 (Batch 가 구매한 제품 수량)

        self._allocations: Set[OrderLine] = set()  # 할당된 OrderLine 집합

    @property
    def allocated_quantity(self) -> int:
        return sum(_line.qty for _line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def allocate(self, line: OrderLine):
        """
        OrderLine 을 할당한다.
        할당 후에는 사용 가능한 수량이 줄어든다.
        :param line: OrderLine
        """
        if not self.can_allocate(line):
            raise ValueError("Cannot allocate line")
        self._allocations.add(line)

    def can_allocate(self, line: OrderLine) -> bool:
        """
        OrderLine 을 할당할 수 있는지 여부를 반환한다.
        :param line: OrderLine
        :return: bool
        """
        if line.sku != self.sku:
            return False

        return self.available_quantity >= line.qty

    def deallocate(self, line: OrderLine):
        """
        OrderLine 을 할당 해제한다.
        할당 해제 후에는 사용 가능한 수량이 증가한다.
        단, 자신에게 할당되지 않은 OrderLine 을 할당 해제하면, 수량 변화가 없다.
        """
        if line in self._allocations:
            self._allocations.remove(line)
