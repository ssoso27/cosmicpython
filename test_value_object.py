import pytest
from dataclasses import dataclass
from typing import NamedTuple
from collections import namedtuple


@dataclass(frozen=True)
class Name:
    first_name: str
    surname: str


class Money(NamedTuple):
    currency: str
    value: int


Line = namedtuple('Line', ['sku', 'qty'])


def test_equality_name():
    assert Name('SOHEE', 'YANG') == Name('SOHEE', 'YANG')
    assert Name('SOHEE', 'YANG') != Name('SOHEE', 'KIM')


def test_equality_money():
    assert Money('USD', 100) == Money('USD', 100)
    assert Money('USD', 100) != Money('KRW', 100)


def test_equality_line():
    assert Line('BLUE-HAMSTER', 10) == Line('BLUE-HAMSTER', 10)
    assert Line('BLUE-HAMSTER', 10) != Line('RED-HAMSTER', 10)
    assert Line('BLUE-HAMSTER', 10) != Line('BLUE-HAMSTER', 20)
    assert Line('BLUE-HAMSTER', 10) != Line('blue-hamster', 10)


"""
Value Object 는 복잡한 동작을 수행할 수 있다.
값에 대한 연산을 지원하는 것이 일반적이다. (예: 수학 연산자)


won_500 = Money('KRW', 500)
won_1000 = Money('KRW', 1000)


def test_can_add_money_values_for_the_same_currency():
    assert won_500 + won_500 == won_1000


def test_can_subtract_money_values():
    assert won_1000 - won_500 == won_500


def test_adding_different_currencies_fails():
    with pytest.raises(ValueError):
        Money('KRW', 500) + Money('USD', 500)


def test_can_multiply_money_by_a_number():
    assert won_500 * 5 == Money('KRW', 2500)


def test_multiplying_tow_money_values_is_an_error():
    with pytest.raises(TypeError):
        won_500 * won_500
"""


class Person:
    def __init__(self, name: Name):
        self.name = name


def test_barry_is_harry():
    harry = Person(Name('Harry', 'Potter'))
    barry = harry
    barry.name = Name('Barry', 'Trotter')
    assert barry == harry  # identity equality
