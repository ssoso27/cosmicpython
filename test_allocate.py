"""
도메인 서비스에 대한 단독 함수 allocate() 테스트
"""
import pytest
from datetime import date, timedelta
from model import Batch, OrderLine, allocate
from my_exceptions import AllocateError

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    """
    창고에 도착한 Batch (current stock) 와 아직 도착하지 않은 Batch (shipment) 가 있을 때,
    현재 창고에 있는 Batch 를 우선적으로 사용한다.
    """
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", eta=None, qty=100)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", eta=later, qty=100)

    line = OrderLine("orderid", "RETRO-CLOCK", 10)

    allocate(line, [shipment_batch, in_stock_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    """
    모든 Batch 가 배송중이라면, 가장 먼저 도착하는 Batch 를 사용한다.
    """
    today_batch = Batch("today-batch", "RETRO-CLOCK", eta=today, qty=100)
    tomorrow_batch = Batch("tomorrow-batch", "RETRO-CLOCK", eta=tomorrow, qty=100)
    later_batch = Batch("later-batch", "RETRO-CLOCK", eta=later, qty=100)

    line = OrderLine("orderid", "RETRO-CLOCK", 10)

    allocate(line, [tomorrow_batch, today_batch, later_batch])

    assert today_batch.available_quantity == 90
    assert tomorrow_batch.available_quantity == 100
    assert later_batch.available_quantity == 100


def test_returns_allocated_batch_ref():
    """
    allocate() 메서드는 할당된 Batch 의 참조 번호를 반환한다.
    """
    batch1 = Batch("batch1-ref", "RETRO-CLOCK", eta=today, qty=100)
    line = OrderLine("orderid", "RETRO-CLOCK", 10)

    allocated_ref = allocate(line, [batch1])

    assert allocated_ref == batch1.reference


def test_raises_allocate_error_if_cannot_allocate():
    """
    모든 Batch 에서 주문 라인을 할당할 수 없다면, AllocateError 예외를 발생시킨다.
    """
    with pytest.raises(AllocateError):
        batches = [
            Batch("batch1-ref", "RETRO-CLOCK", eta=today, qty=100),
            Batch("batch2-ref", "RETRO-CLOCK", eta=today, qty=100),
        ]
        line = OrderLine("orderid", "BLUE-CLOCK", 10)
        allocate(line, batches)
