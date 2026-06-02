#!/usr/bin/env python3
"""
AI Crypto Trading Bot - Main Engine
Author: kawser parvez
Email: kawserparvez7878@gmail.com
"""

import time
import logging
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config import (
    BINANCE_API_KEY, BINANCE_SECRET_KEY,
    TRADING_PAIRS, CHECK_INTERVAL, TRADE_QUANTITY,
    LOG_LEVEL, LOG_FILE
)
from technical_analysis import TechnicalAnalysis
from ml_model import MLModel
from telegram_handler import TelegramHandler

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class CryptoTradingBot:
    def __init__(self):
        logger.info("Initializing AI Crypto Trading Bot...")
        self.client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
        self.ta = TechnicalAnalysis()
        self.ml = MLModel()
        self.telegram = TelegramHandler()
        self.active_trades = {}
        self.performance = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0
        }
        logger.info("Bot initialized successfully.")

    def get_klines(self, symbol, interval='1h', limit=200):
        try:
            return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        except BinanceAPIException as e:
            logger.error(f"Binance API error for {symbol}: {e}")
            return None

    def get_current_price(self, symbol):
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return 0.0

    def get_account_balance(self, asset='USDT'):
        try:
            balance = self.client.get_asset_balance(asset=asset)
            return float(balance['free'])
        except BinanceAPIException as e:
            logger.error(f"Error fetching balance: {e}")
            return 0.0

    def generate_signal(self, symbol):
        klines = self.get_klines(symbol)
        if klines is None:
            return {'signal': 'HOLD', 'confidence': 0.0}
        ta_signal = self.ta.analyze(klines)
        ml_prediction = self.ml.predict(klines)
        signal = self._combine_signals(ta_signal, ml_prediction)
        current_price = self.get_current_price(symbol)
        result = {
            'symbol': symbol,
            'signal': signal['action'],
            'confidence': signal['confidence'],
            'current_price': current_price,
            'ta_signal': ta_signal,
            'ml_prediction': ml_prediction,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.info(f"Signal for {symbol}: {result['signal']} (confidence: {result['confidence']:.2f})")
        return result

    def _combine_signals(self, ta_signal, ml_prediction):
        ta_score = ta_signal.get('score', 0)
        ml_score = ml_prediction.get('score', 0)
        combined = (ta_score * 0.4) + (ml_score * 0.6)
        confidence = abs(combined)
        if combined > 0.3:
            action = 'BUY'
        elif combined < -0.3:
            action = 'SELL'
        else:
            action = 'HOLD'
        return {'action': action, 'confidence': round(confidence, 4)}

    def execute_trade(self, symbol, signal):
        action = signal['signal']
        confidence = signal['confidence']
        if confidence < 0.5:
            logger.info(f"Skipping {action} for {symbol} - low confidence ({confidence:.2f})")
            return
        try:
            if action == 'BUY':
                order = self.client.order_market_buy(
                    symbol=symbol,
                    quantity=TRADE_QUANTITY.get(symbol, 0.001)
                )
                logger.info(f"BUY order placed for {symbol}: {order}")
                self.active_trades[symbol] = {
                    'entry_price': signal['current_price'],
                    'order_id': order['orderId']
                }
                self.telegram.send_trade_signal(signal, order)
            elif action == 'SELL' and symbol in self.active_trades:
                order = self.client.order_market_sell(
                    symbol=symbol,
                    quantity=TRADE_QUANTITY.get(symbol, 0.001)
                )
                logger.info(f"SELL order placed for {symbol}: {order}")
                self._record_trade_result(symbol, signal['current_price'])
                self.telegram.send_trade_signal(signal, order)
                del self.active_trades[symbol]
        except BinanceAPIException as e:
            logger.error(f"Trade execution error for {symbol}: {e}")
            self.telegram.send_error_alert(str(e))

    def _record_trade_result(self, symbol, exit_price):
        if symbol not in self.active_trades:
            return
        entry = self.active_trades[symbol]['entry_price']
        pnl = exit_price - entry
        self.performance['total_trades'] += 1
        self.performance['total_profit'] += pnl
        if pnl > 0:
            self.performance['winning_trades'] += 1
        else:
            self.performance['losing_trades'] += 1

    def send_performance_report(self):
        total = self.performance['total_trades']
        win_rate = (self.performance['winning_trades'] / total * 100) if total > 0 else 0
        report = (
            f"Performance Report\n"
            f"Total Trades: {total}\n"
            f"Winning: {self.performance['winning_trades']}\n"
            f"Losing: {self.performance['losing_trades']}\n"
            f"Win Rate: {win_rate:.1f}%\n"
            f"Total PnL: {self.performance['total_profit']:.4f} USDT"
        )
        self.telegram.send_message(report)

    def run(self):
        logger.info("Starting 24/7 market monitoring...")
        self.telegram.send_message("AI Crypto Trading Bot is now LIVE and monitoring markets 24/7!")
        report_counter = 0
        while True:
            try:
                for symbol in TRADING_PAIRS:
                    signal = self.generate_signal(symbol)
                    self.execute_trade(symbol, signal)
                    time.sleep(1)
                report_counter += 1
                if report_counter >= 24:
                    self.send_performance_report()
                    report_counter = 0
                logger.info(f"Cycle complete. Sleeping {CHECK_INTERVAL}s...")
                time.sleep(CHECK_INTERVAL)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user.")
                self.telegram.send_message("Trading bot stopped manually.")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                self.telegram.send_error_alert(str(e))
                time.sleep(60)


if __name__ == '__main__':
    bot = CryptoTradingBot()
    bot.run()
