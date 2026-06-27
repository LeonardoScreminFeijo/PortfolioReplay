from datetime import date
from typing import Protocol


class RebalanceStrategy(Protocol):
    def should_rebalance(self, current_date: date, prev_date: date | None) -> bool: ...


class NoRebalance:
    def should_rebalance(self, current_date: date, prev_date: date | None) -> bool:
        return False


class MonthlyRebalance:
    def should_rebalance(self, current_date: date, prev_date: date | None) -> bool:
        if prev_date is None:
            return False
        return current_date.month != prev_date.month or current_date.year != prev_date.year


class QuarterlyRebalance:
    def should_rebalance(self, current_date: date, prev_date: date | None) -> bool:
        if prev_date is None:
            return False
        current_quarter = (current_date.month - 1) // 3
        prev_quarter = (prev_date.month - 1) // 3
        return current_quarter != prev_quarter or current_date.year != prev_date.year
