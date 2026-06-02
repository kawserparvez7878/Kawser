# 🤖 AI Crypto Trading Bot

> An AI-powered cryptocurrency trading bot with Binance API integration, advanced technical analysis, LSTM neural network price prediction, and real-time Telegram notifications.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13+-orange.svg)](https://tensorflow.org)
[![Binance](https://img.shields.io/badge/Binance-API-yellow.svg)](https://binance.com)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Trading Strategy](#trading-strategy)
- [ML Model](#ml-model)
- [Risk Management](#risk-management)
- [Disclaimer](#disclaimer)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔄 **24/7 Monitoring** | Continuously scans cryptocurrency markets |
| 📊 **Technical Analysis** | MA, RSI, MACD, Bollinger Bands indicators |
| 🧠 **ML Predictions** | LSTM neural network for price forecasting |
| 📱 **Telegram Alerts** | Real-time BUY/SELL signals to @CodeReceiveBot |
| 💹 **Multi-Pair Support** | BTC, ETH, BNB, SOL, ADA, XRP, DOGE, MATIC |
| 🛡️ **Risk Management** | Stop-loss, take-profit, confidence thresholds |
| 📈 **Performance Reports** | Automated win rate and PnL reporting |
| 🔁 **Auto Retraining** | ML model retrains on fresh market data |

---

## 📁 Project Structure

```
crypto-ai-trader/
├── trading_bot.py          # Main trading engine & 24/7 loop
├── ml_model.py             # LSTM neural network for price prediction
├── technical_analysis.py   # TA indicators (MA, RSI, MACD, BB)
├── telegram_handler.py     # Telegram notification system
├── config.py               # Configuration & API credentials
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── models/
│   └── lstm_crypto_model.h5  # Saved ML model
└── logs/
    └── trading_bot.log       # Application logs
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Binance account with API access
- Telegram bot token

### Step 1: Clone the Repository
```bash
git clone https://github.com/kawserparvez7878/Kawser.git
cd Kawser
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create Required Directories
```bash
mkdir -p models logs
```

---

## ⚙️ Configuration

### Option 1: Environment Variables (Recommended)
Create a `.env` file in the project root:
```env
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=@YourTelegramChannel
```

### Option 2: Edit config.py Directly
Open `config.py` and replace the placeholder values:
```python
BINANCE_API_KEY = 'your_actual_api_key'
BINANCE_SECRET_KEY = 'your_actual_secret_key'
TELEGRAM_BOT_TOKEN = 'your_bot_token'
TELEGRAM_CHAT_ID = '@CodeReceiveBot'
```

### Key Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `CHECK_INTERVAL` | 3600 | Seconds between market scans |
| `MIN_CONFIDENCE` | 0.5 | Minimum signal confidence to trade |
| `STOP_LOSS_PCT` | 0.02 | Stop-loss at 2% |
| `TAKE_PROFIT_PCT` | 0.05 | Take-profit at 5% |
| `ML_LOOKBACK` | 60 | Candles used for ML prediction |
| `ML_EPOCHS` | 100 | LSTM training epochs |

---

## 🎮 Usage

### Start the Bot
```bash
python trading_bot.py
```

### Train ML Model Only
```python
from ml_model import MLModel
from binance.client import Client

client = Client(api_key, api_secret)
klines = client.get_klines(symbol='BTCUSDT', interval='1h', limit=1000)

ml = MLModel()
ml.train(klines)
ml.save()
```

### Run Technical Analysis Only
```python
from technical_analysis import TechnicalAnalysis

ta = TechnicalAnalysis()
result = ta.analyze(klines)
print(result)
```

---

## 🔬 How It Works

```
┌─────────────────────────────────────────────────────┐
│                  TRADING CYCLE                       │
│                                                     │
│  1. Fetch OHLCV data from Binance API               │
│         ↓                                           │
│  2. Technical Analysis (MA + RSI + MACD + BB)       │
│         ↓                                           │
│  3. LSTM ML Prediction (price direction)            │
│         ↓                                           │
│  4. Combine signals (40% TA + 60% ML)               │
│         ↓                                           │
│  5. Generate BUY / SELL / HOLD signal               │
│         ↓                                           │
│  6. Execute trade if confidence >= 50%              │
│         ↓                                           │
│  7. Send Telegram notification                      │
│         ↓                                           │
│  8. Wait → Repeat every hour                        │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Trading Strategy

### Signal Combination
The bot combines two signal sources with weighted scoring:
- **Technical Analysis (40%)**: MA crossovers, RSI levels, MACD crossovers, Bollinger Band breakouts
- **ML Prediction (60%)**: LSTM neural network predicts next candle direction

### Signal Thresholds
| Combined Score | Action |
|---------------|--------|
| > +0.3 | **BUY** |
| < -0.3 | **SELL** |
| -0.3 to +0.3 | **HOLD** |

---

## 🧠 ML Model

The LSTM model architecture:
```
Input (60 candles × 11 features)
    ↓
LSTM(128) → BatchNorm → Dropout(0.2)
    ↓
LSTM(64)  → BatchNorm → Dropout(0.2)
    ↓
LSTM(32)  → BatchNorm → Dropout(0.2)
    ↓
Dense(32, relu) → Dense(16, relu)
    ↓
Dense(1, linear) → Price Prediction
```

**Features used:** Open, High, Low, Close, Volume, Returns, HL Ratio, OC Ratio, Volume MA, Price MA5, Price MA20

---

## 🛡️ Risk Management

- **Confidence Filter**: Only trades with ≥50% confidence are executed
- **Stop-Loss**: Automatic 2% stop-loss on all positions
- **Take-Profit**: Automatic 5% take-profit target
- **Max Open Trades**: Limited to 3 simultaneous positions
- **Error Handling**: All exceptions caught and reported via Telegram

---

## ⚠️ Disclaimer

> **This bot is for educational purposes only. Cryptocurrency trading involves significant financial risk. Past performance does not guarantee future results. Never invest more than you can afford to lose. The authors are not responsible for any financial losses incurred through the use of this software.**

---

## 👤 Author

**kawser parvez**
- Email: kawserparvez7878@gmail.com
- Telegram: @CodeReceiveBot
- GitHub: [kawserparvez7878](https://github.com/kawserparvez7878)

---

*Built with ❤️ using Python, TensorFlow, and Binance API*
