from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD, ATR
from surmount.data import Asset
from surmount.logging import log

class TradingStrategy(Strategy):
    """
    Trading strategy that seeks to capture momentum while managing risk through volatility adjustment.
    - Enters a position with MACD crossover: buys when the MACD line crosses above the signal line,
      indicating upward momentum.
    - Exits a position or reduces allocation when the ATR indicates high volatility,
      suggesting potential drawdown risk.
    """

    def __init__(self):
        self.tickers = ["SPY"]  # Focused on the SPY ETF for demonstration. Adjust as needed.

    @property
    def assets(self):
        """List of assets to trade."""
        return self.tickers

    @property
    def interval(self):
        """Data interval for indicators calculation."""
        return "1day"

    def run(self, data):
        """
        Executes the trading logic at each trading interval.
        :param data: The market data and indicators for the assets.
        :return: TargetAllocation with the desired portfolio allocation.
        """
        allocation_dict = {}

        for ticker in self.tickers:
            macd_data = MACD(ticker, data["ohlcv"], fast=12, slow=26)
            atr_data = ATR(ticker, data["ohlcv"], length=14)

            if macd_data is None or atr_data is None:
                log(f"Insufficient data for {ticker}")
                continue

            # MACD buy signal: MACD line crosses above signal line
            macd_line = macd_data["MACD"][-1]
            signal_line = macd_data["signal"][-1]
            # Volatility filter: lower allocation if current ATR is higher than recent average
            current_atr = atr_data[-1]
            avg_atr = sum(atr_data[-14:]) / 14  # 2-week average

            if macd_line > signal_line and current_atr <= avg_atr:
                # Strong upward momentum and acceptable volatility
                allocation = 1.0
            elif macd_line < signal_line or current_atr > avg_atr:
                # Downward momentum or high volatility
                allocation = 0.0  # Exit or avoid position
            else:
                # Neutral condition, maintain current position
                # This example always enters a clear state; adjust logic for more nuanced handling
                allocation = 0.0

            allocation_dict[ticker] = allocation

        return TargetAllocation(allocation_dict)