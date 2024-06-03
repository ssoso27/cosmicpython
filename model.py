from typing import Optional, Set, List
from dataclasses import dataclass
from datetime import date, timedelta
from my_exceptions import AllocateError


@dataclass(frozen=True)  # OrderLine 은 동작이 없는 불변 데이터 클래스다.
class OrderLine:
    """
    OrderLine 은 Value Object 이다.
    """
    orderid: str  # 주문 번호
    sku: str  # 제품 식별자
    qty: int  # 주문 수량

    """
    Value Object 는 모든 값 속성을 사용하여 해시를 정의해야 한다.
    def __hash__(self):
        return hash(self.orderid + self.sku + str(self.qty))
    """


class Batch:
    """
    Batch 는 Entity 이다.
    Batcn 의 정체성은 Batch 참조 번호(reference)로 식별한다.
    """
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref  # Batch 참조 번호
        self.sku = sku  # 제품 식별자
        self.eta = eta  # 예상 도착일
        self._purchased_quantity = qty  # 구매 수량 (Batch 가 구매한 제품 수량)

        self._allocations: Set[OrderLine] = set()  # 할당된 OrderLine 집합

    def __eq__(self, other):
        """
        __eq__() : == 연산자를 사용할 때 호출되는 매직 메서드
        동등성 연산자(__eq__)를 구현 -> 정체성 동등성 (identity equality)을 사용한다.
        """
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        """
        __hash__() : 객체를 집합에 추가하거나 딕셔너리의 키로 사용할 때 동작을 제어하기 위해 사용하는 매직 메서드
        시간과 무관하게 Entity 의 정체성을 식별해주는 속성을 사용하여 정의해야 한다.
        """
        return hash(self.reference)

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
            raise AllocateError("Cannot allocate line")
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


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    """
    모든 재고를 표현하는 구체적인 Batch 집합에서 OrderLine 을 할당하는 도메인 서비스 함수
    :param line: OrderLine
    :param batches: List[Batch]  (Why not Set[Batch]?)
    :return: 할당된 Batch 의 참조 번호
    """
    already = date.today() - timedelta(days=1)
    batches = sorted(batches, key=lambda x: x.eta or already)  # None 을 처리하기 위해 기본값을 설정한다.
    for b in batches:
        if b.can_allocate(line):
            b.allocate(line)
            return b.reference
    else:
        raise AllocateError("All batches cannot allocate the line")
