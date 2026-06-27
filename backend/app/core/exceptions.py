class PortfolioReplayError(Exception):
    pass


class TickerNotFoundError(PortfolioReplayError):
    pass


class DataProviderError(PortfolioReplayError):
    pass


class DateRangeError(PortfolioReplayError):
    pass
