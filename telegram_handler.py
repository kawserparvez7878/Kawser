#!/usr/bin/env python3
"""
Telegram Handler - Notification System
Author: kawser parvez
Description: Sends trading signals, alerts, and performance reports
             to @CodeReceiveBot via Telegram.
"""

import logging
import requests
from datetime import datetime
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


class TelegramHandler:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        logger.info("Telegram handler initialized.")

    def send_message(self, text, parse_mode='Markdown'):
        """Send a plain text message."""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.debug(f"Telegram message sent: {text[:50]}...")
            return response.json()
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return None

    def send_trade_signal(self, signal, order=None):
        """Send a formatted trading signal notification."""
        action = signal.get('signal', 'UNKNOWN')
        symbol = signal.get('symbol', 'N/A')
        price = signal.get('current_price', 0)
        confidence = signal.get('confidence', 0)
        timestamp = signal.get('timestamp', datetime.utcnow().isoformat())

        emoji = 'BUY' and '\U0001F7E2' if action == 'BUY' else ('\U0001F534' if action == 'SELL' else '\U0001F7E1')

        msg = (
            f"{emoji} *TRADING SIGNAL*\n"
            f"{'='*30}\n"
            f"*Pair:* `{symbol}`\n"
            f"*Action:* *{action}*\n"
            f"*Price:* `${price:,.4f}`\n"
            f"*Confidence:* `{confidence:.1%}`\n"
        )

        ta = signal.get('ta_signal', {})
        if ta:
            msg += (
                f"\n*Technical Analysis:*\n"
                f"  RSI: `{ta.get('rsi_value', 'N/A')}`\n"
                f"  MACD: `{ta.get('macd_value', 'N/A')}`\n"
                f"  MA Score: `{ta.get('ma_score', 'N/A')}`\n"
            )

        ml = signal.get('ml_prediction', {})
        if ml:
            msg += (
                f"\n*ML Prediction:*\n"
                f"  Direction: `{ml.get('direction', 'N/A')}`\n"
                f"  Predicted Change: `{ml.get('predicted_change_pct', 'N/A')}%`\n"
            )

        if order:
            msg += f"\n*Order ID:* `{order.get('orderId', 'N/A')}`\n"

        msg += f"\n*Time:* `{timestamp}`"
        return self.send_message(msg)

    def send_performance_report(self, performance):
        """Send a detailed performance report."""
        total = performance.get('total_trades', 0)
        winning = performance.get('winning_trades', 0)
        losing = performance.get('losing_trades', 0)
        profit = performance.get('total_profit', 0.0)
        win_rate = (winning / total * 100) if total > 0 else 0

        msg = (
            f"\U0001F4CA *PERFORMANCE REPORT*\n"
            f"{'='*30}\n"
            f"*Total Trades:* `{total}`\n"
            f"*Winning:* `{winning}` \U0001F7E2\n"
            f"*Losing:* `{losing}` \U0001F534\n"
            f"*Win Rate:* `{win_rate:.1f}%`\n"
            f"*Total PnL:* `{profit:+.4f} USDT`\n"
            f"*Generated:* `{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}`"
        )
        return self.send_message(msg)

    def send_error_alert(self, error_msg):
        """Send an error/alert notification."""
        msg = (
            f"\u26A0\uFE0F *BOT ALERT*\n"
            f"{'='*30}\n"
            f"*Error:* `{error_msg[:200]}`\n"
            f"*Time:* `{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}`"
        )
        return self.send_message(msg)

    def send_startup_message(self):
        """Send bot startup notification."""
        msg = (
            f"\U0001F916 *AI CRYPTO TRADING BOT STARTED*\n"
            f"{'='*30}\n"
            f"Status: *LIVE*\n"
            f"Monitoring: 24/7\n"
            f"Started: `{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}`\n"
            f"\nBot is now analyzing markets and generating signals!"
        )
        return self.send_message(msg)
