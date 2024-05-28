from datetime import date, timedelta
import pytest

# from model import ...
from model import Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


"""
Test Batch.allocate() method
"""


def test_allocating_to_a_batch_reduces_the_available_quantity():
    """
    20단위의 SMALL-TABLE로 이루어진 배치가 있고, 2단위의 SMALL-TABLE을 요구하는 주문 라인이 있다.
    주문 라인을 할당하면, 배치에 18단위의 SMALL-TABLE이 남아있어야 한다.
    """
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=today)
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_allocate_add_order_line_to_allocations():
    """
    OrderLine 을 할당하면, Batch._allocations 에 OrderLine 이 추가된다.
    """
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=today)
    line = OrderLine("order-ref", "SMALL-TABLE", 10)

    batch._allocations = set()  # reset allocations
    batch.allocate(line)

    assert line in batch._allocations


def test_allocation_is_idempotent():
    """
    이미 할당된 OrderLine 을 다시 할당하면, 아무런 변화가 없어야 한다. (멱등)
    """
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=today)
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 18


"""
Test Batch.can_allocate() method
"""


def test_can_allocate_if_available_greater_than_required():
    """
    Batch.available_quantity 가 OrderLine.qty 보다 크면 할당할 수 있다.
    """
    batch = Batch("batch-001", "SMALL-TABLE", qty=10, eta=today)
    line = OrderLine("order-ref", "SMALL-TABLE", 5)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_available_smaller_than_required():
    """
    Batch.available_quantity 가 OrderLine.qty 보다 작으면 할당할 수 없다.
    """
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=today)
    line = OrderLine("order-ref", "SMALL-TABLE", 30)

    assert not batch.can_allocate(line)


def test_can_allocate_if_available_equal_to_required():
    """
    Batch.available_quantity 가 OrderLine.qty 와 같으면 할당할 수 있다.
    """
    batch = Batch("batch-001", "SMALL-TABLE", qty=10, eta=today)
    line = OrderLine("order-ref", "SMALL-TABLE", 10)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    """
    Batch.sku 와 OrderLine.sku 가 다르면 할당할 수 없다.
    """
    batch = Batch("batch-001", "SMALL-TABLE", qty=10, eta=today)
    line = OrderLine("order-ref", "LARGE-TABLE", 10)

    assert not batch.can_allocate(line)


"""
Test Batch.deallocate() method
"""


def test_deallocate_and_increase_available_quantity():
    """
    할당된 OrderLine 을 할당 해제하면, Batch.available_quantity 가 증가한다.
    """
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=today)
    allocated_line = OrderLine("order-ref", "SMALL-TABLE", 2)
    batch._allocations = {allocated_line}

    before_deallocate = batch.available_quantity
    batch.deallocate(allocated_line)
    assert batch.available_quantity == before_deallocate + 2


def test_deallocate_does_not_increase_available_quantity_if_line_not_allocated():
    """
    할당되지 않은 OrderLine 을 할당 해제하면, Batch.available_quantity 가 변하지 않는다.
    """
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=today)
    unallocated_line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_deallocate_is_idempotent():
    """
    이미 할당 해제된 OrderLine 을 다시 할당 해제하면, 아무런 변화가 없어야 한다. (멱등)
    """
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=today)
    allocated_line = OrderLine("order-ref", "SMALL-TABLE", 2)
    batch._allocations = {allocated_line}

    before_deallocate = batch.available_quantity
    batch.deallocate(allocated_line)
    batch.deallocate(allocated_line)

    assert batch.available_quantity == before_deallocate + 2


def test_prefers_warehouse_batches_to_shipments():
    pytest.fail("todo")


def test_prefers_earlier_batches():
    pytest.fail("todo")
