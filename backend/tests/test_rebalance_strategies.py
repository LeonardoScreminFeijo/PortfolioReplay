from datetime import date

import pytest

from app.services.rebalance_strategies import MonthlyRebalance, NoRebalance, QuarterlyRebalance


def test_no_rebalance_never_triggers() -> None:
    s = NoRebalance()
    assert not s.should_rebalance(date(2024, 1, 15), date(2024, 1, 14))
    assert not s.should_rebalance(date(2024, 2, 1), date(2024, 1, 31))
    assert not s.should_rebalance(date(2024, 1, 2), None)


def test_monthly_triggers_on_new_month() -> None:
    s = MonthlyRebalance()
    assert s.should_rebalance(date(2024, 2, 1), date(2024, 1, 31))
    assert s.should_rebalance(date(2024, 3, 1), date(2024, 2, 29))


def test_monthly_does_not_trigger_same_month() -> None:
    s = MonthlyRebalance()
    assert not s.should_rebalance(date(2024, 1, 15), date(2024, 1, 14))
    assert not s.should_rebalance(date(2024, 1, 31), date(2024, 1, 2))


def test_monthly_no_trigger_on_first_day() -> None:
    s = MonthlyRebalance()
    assert not s.should_rebalance(date(2024, 1, 2), None)


def test_monthly_triggers_on_new_year() -> None:
    s = MonthlyRebalance()
    assert s.should_rebalance(date(2025, 1, 2), date(2024, 12, 31))


@pytest.mark.parametrize(
    "current,prev,expected",
    [
        (date(2024, 4, 1), date(2024, 3, 31), True),   # Q2 start
        (date(2024, 7, 1), date(2024, 6, 28), True),   # Q3 start
        (date(2024, 10, 1), date(2024, 9, 30), True),  # Q4 start
        (date(2025, 1, 2), date(2024, 12, 31), True),  # Q1 new year
        (date(2024, 2, 1), date(2024, 1, 31), False),  # same quarter
        (date(2024, 3, 15), date(2024, 1, 2), False),  # same quarter
        (date(2024, 4, 1), None, False),                # first day
    ],
)
def test_quarterly(current: date, prev: date | None, expected: bool) -> None:
    s = QuarterlyRebalance()
    assert s.should_rebalance(current, prev) == expected
