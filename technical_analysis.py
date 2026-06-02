#!/usr/bin/env python3
"""
Technical Analysis Module
Author: kawser parvez
Description: Moving Average, RSI, MACD indicators and signal generation.
"""

import numpy as np
import pandas as pd
import logging
from config import TA_MA_SHORT, TA_MA_LONG, TA_RSI_PERIOD, TA_MACD_FAST, TA_MACD_SLOW, TA_MACD_SIGNAL

logger = logging.getLogger(__name__)


class TechnicalAnalysis:
    def __init__(self):
        self.ma_short = TA_MA_SHORT
        self.ma_long = TA_MA_LONG
        self.rsi_period = TA_RSI_PERIOD
        self.macd_fast = TA_MACD_FAST
        self.macd_slow = TA_MACD_SLOW
        self.macd_signal = TA_MACD_SIGNAL

    def _klines_to_series(self, klines):
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df

    # --- Moving Averages ---
    def moving_average(self, series, period):
        return series.rolling(window=period).mean()

    def ema(self, series, period):
        return series.ewm(span=period, adjust=False).mean()

    def ma_signal(self, df):
        ma_short = self.moving_average(df['close'], self.ma_short)
        ma_long = self.moving_average(df['close'], self.ma_long)
        latest_short = ma_short.iloc[-1]
        latest_long = ma_long.iloc[-1]
        prev_short = ma_short.iloc[-2]
        prev_long = ma_long.iloc[-2]
        # Golden cross = BUY, Death cross = SELL
        if prev_short <= prev_long and latest_short > latest_long:
            return 1.0   # Strong BUY
        elif prev_short >= prev_long and latest_short < latest_long:
            return -1.0  # Strong SELL
        elif latest_short > latest_long:
            return 0.5   # Weak BUY
        else:
            return -0.5  # Weak SELL

    # --- RSI ---
    def rsi(self, series, period=None):
        period = period or self.rsi_period
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def rsi_signal(self, df):
        rsi_values = self.rsi(df['close'])
        latest_rsi = rsi_values.iloc[-1]
        if latest_rsi < 30:
            return 1.0   # Oversold -> BUY
        elif latest_rsi > 70:
            return -1.0  # Overbought -> SELL
        elif latest_rsi < 45:
            return 0.3
        elif latest_rsi > 55:
            return -0.3
        else:
            return 0.0   # Neutral

    # --- MACD ---
    def macd(self, series):
        ema_fast = self.ema(series, self.macd_fast)
        ema_slow = self.ema(series, self.macd_slow)
        macd_line = ema_fast - ema_slow
        signal_line = self.ema(macd_line, self.macd_signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def macd_signal_score(self, df):
        macd_line, signal_line, histogram = self.macd(df['close'])
        latest_hist = histogram.iloc[-1]
        prev_hist = histogram.iloc[-2]
        latest_macd = macd_line.iloc[-1]
        latest_signal = signal_line.iloc[-1]
        # Bullish crossover
        if prev_hist < 0 and latest_hist > 0:
            return 1.0
        # Bearish crossover
        elif prev_hist > 0 and latest_hist < 0:
            return -1.0
        elif latest_macd > latest_signal:
            return 0.4
        else:
            return -0.4

    # --- Bollinger Bands ---
    def bollinger_bands(self, series, period=20, std_dev=2):
        ma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = ma + (std * std_dev)
        lower = ma - (std * std_dev)
        return upper, ma, lower

    def bollinger_signal(self, df):
        upper, mid, lower = self.bollinger_bands(df['close'])
        latest_close = df['close'].iloc[-1]
        if latest_close < lower.iloc[-1]:
            return 0.8   # Price below lower band -> BUY
        elif latest_close > upper.iloc[-1]:
            return -0.8  # Price above upper band -> SELL
        else:
            return 0.0

    # --- Combined Analysis ---
    def analyze(self, klines):
        try:
            df = self._klines_to_series(klines)
            ma_score = self.ma_signal(df)
            rsi_score = self.rsi_signal(df)
            macd_score = self.macd_signal_score(df)
            bb_score = self.bollinger_signal(df)

            # Weighted combination
            combined_score = (
                ma_score * 0.30 +
                rsi_score * 0.25 +
                macd_score * 0.30 +
                bb_score * 0.15
            )

            rsi_values = self.rsi(df['close'])
            macd_line, signal_line, histogram = self.macd(df['close'])

            result = {
                'score': round(combined_score, 4),
                'ma_score': round(ma_score, 4),
                'rsi_score': round(rsi_score, 4),
                'macd_score': round(macd_score, 4),
                'bb_score': round(bb_score, 4),
                'rsi_value': round(rsi_values.iloc[-1], 2),
                'macd_value': round(macd_line.iloc[-1], 6),
                'macd_signal_value': round(signal_line.iloc[-1], 6),
                'macd_histogram': round(histogram.iloc[-1], 6),
                'current_price': df['close'].iloc[-1]
            }
            logger.debug(f"TA analysis complete: score={combined_score:.4f}")
            return result
        except Exception as e:
            logger.error(f"Technical analysis error: {e}")
            return {'score': 0.0}
