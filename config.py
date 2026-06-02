#!/usr/bin/env python3
"""
Configuration File - AI Crypto Trading Bot
Author: kawser parvez
Email: kawserparvez7878@gmail.com
Description: All API keys, trading parameters, and ML model settings.
             Replace placeholder values with your actual credentials.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# BINANCE API CREDENTIALS
# ============================================================
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'YOUR_BINANCE_API_KEY_HERE')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', 'YOUR_BINANCE_SECRET_KEY_HERE')

# ============================================================
# TELEGRAM CONFIGURATION
# ============================================================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8723812816:AAFov0BuNE3bJdmhSjN2wPH4FYa-MaYFLyI')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '@CodeReceiveBot')

# ============================================================
# TRADING PARAMETERS
# ============================================================
# Cryptocurrency pairs to monitor
TRADING_PAIRS = [
    'BTCUSDT',
    'ETHUSDT',
    'BNBUSDT',
    'SOLUSDT',
    'ADAUSDT',
    'XRPUSDT',
    'DOGEUSDT',
    'MATICUSDT',
]

# Trade quantity per pair (in base asset units)
TRADE_QUANTITY = {
    'BTCUSDT':  0.001,
    'ETHUSDT':  0.01,
    'BNBUSDT':  0.1,
    'SOLUSDT':  0.1,
    'ADAUSDT':  10.0,
    'XRPUSDT':  10.0,
    'DOGEUSDT': 100.0,
    'MATICUSDT': 10.0,
}

# Interval between market scan cycles (seconds)
CHECK_INTERVAL = 3600  # 1 hour

# Minimum confidence threshold to execute a trade (0.0 - 1.0)
MIN_CONFIDENCE = 0.5

# Maximum open trades at once
MAX_OPEN_TRADES = 3

# Stop-loss percentage
STOP_LOSS_PCT = 0.02   # 2%

# Take-profit percentage
TAKE_PROFIT_PCT = 0.05  # 5%

# ============================================================
# TECHNICAL ANALYSIS PARAMETERS
# ============================================================
TA_MA_SHORT = 9       # Short-term Moving Average period
TA_MA_LONG = 21       # Long-term Moving Average period
TA_RSI_PERIOD = 14    # RSI calculation period
TA_MACD_FAST = 12     # MACD fast EMA period
TA_MACD_SLOW = 26     # MACD slow EMA period
TA_MACD_SIGNAL = 9    # MACD signal line period
TA_BB_PERIOD = 20     # Bollinger Bands period
TA_BB_STD = 2         # Bollinger Bands standard deviation

# ============================================================
# MACHINE LEARNING MODEL SETTINGS
# ============================================================
ML_LOOKBACK = 60          # Number of candles to look back
ML_EPOCHS = 100           # Training epochs
ML_BATCH_SIZE = 32        # Training batch size
ML_LSTM_UNITS = 128       # LSTM units in first layer
ML_DROPOUT_RATE = 0.2     # Dropout rate for regularization
ML_TRAIN_SPLIT = 0.8      # Train/validation split ratio
ML_RETRAIN_INTERVAL = 24  # Retrain every N cycles
MODEL_SAVE_PATH = 'models/lstm_crypto_model.h5'

# ============================================================
# LOGGING SETTINGS
# ============================================================
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/trading_bot.log'

# ============================================================
# BACKTESTING SETTINGS
# ============================================================
BACKTEST_START_DATE = '2024-01-01'
BACKTEST_END_DATE = '2024-12-31'
BACKTEST_INITIAL_CAPITAL = 1000.0  # USDT
