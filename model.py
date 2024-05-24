from typing import Optional
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
        self.available_quantity = qty  # 사용 가능한 수량

    def allocate(self, line: OrderLine):
        """
        OrderLine 을 할당한다.
        할당 후에는 사용 가능한 수량이 줄어든다.
        :param line: OrderLine
        """
        if line.sku != self.sku:
            raise ValueError(f"Invalid sku {line.sku}")
        if self.available_quantity < line.qty:
            raise ValueError("Not enough stock")
        self.available_quantity -= line.qty

    def can_allocate(self, line: OrderLine) -> bool:
        """
        OrderLine 을 할당할 수 있는지 여부를 반환한다.
        :param line: OrderLine
        :return: bool
        """
        if line.sku != self.sku:
            return False

        return self.available_quantity >= line.qty
