#!/usr/bin/env python3
"""
ML Model - LSTM Neural Network for Crypto Price Prediction
Author: kawser parvez
"""

import numpy as np
import pandas as pd
import logging
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from config import ML_LOOKBACK, ML_EPOCHS, ML_BATCH_SIZE, ML_LSTM_UNITS, ML_DROPOUT_RATE, MODEL_SAVE_PATH

logger = logging.getLogger(__name__)


class MLModel:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        self.lookback = ML_LOOKBACK
        self.is_trained = False
        self._try_load_model()

    def build_model(self, input_shape):
        model = Sequential([
            LSTM(ML_LSTM_UNITS, return_sequences=True, input_shape=input_shape),
            BatchNormalization(),
            Dropout(ML_DROPOUT_RATE),
            LSTM(ML_LSTM_UNITS // 2, return_sequences=True),
            BatchNormalization(),
            Dropout(ML_DROPOUT_RATE),
            LSTM(ML_LSTM_UNITS // 4, return_sequences=False),
            BatchNormalization(),
            Dropout(ML_DROPOUT_RATE),
            Dense(32, activation='relu'),
            Dense(16, activation='relu'),
            Dense(1, activation='linear')
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='huber', metrics=['mae'])
        logger.info(f"LSTM model built: {model.count_params()} parameters")
        return model

    def _klines_to_df(self, klines):
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        df['returns'] = df['close'].pct_change()
        df['hl_ratio'] = (df['high'] - df['low']) / df['close']
        df['oc_ratio'] = (df['close'] - df['open']) / df['open']
        df['vol_ma'] = df['volume'].rolling(10).mean()
        df['price_ma5'] = df['close'].rolling(5).mean()
        df['price_ma20'] = df['close'].rolling(20).mean()
        df.dropna(inplace=True)
        return df

    def _prepare_sequences(self, data):
        X, y = [], []
        for i in range(self.lookback, len(data)):
            X.append(data[i - self.lookback:i])
            y.append(data[i, 3])
        return np.array(X), np.array(y)

    def train(self, klines):
        logger.info("Starting LSTM model training...")
        df = self._klines_to_df(klines)
        features = ['open', 'high', 'low', 'close', 'volume', 'returns', 'hl_ratio', 'oc_ratio', 'vol_ma', 'price_ma5', 'price_ma20']
        data = df[features].values
        scaled = self.scaler.fit_transform(data)
        X, y = self._prepare_sequences(scaled)
        split = int(len(X) * 0.8)
        X_train, X_val = X[:split], X[split:]
        y_train, y_val = y[:split], y[split:]
        self.model = self.build_model((X_train.shape[1], X_train.shape[2]))
        callbacks = [
            EarlyStopping(patience=10, restore_best_weights=True),
            ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True)
        ]
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=ML_EPOCHS,
            batch_size=ML_BATCH_SIZE,
            callbacks=callbacks,
            verbose=1
        )
        self.is_trained = True
        self._evaluate(X_val, y_val)
        logger.info("Model training complete.")
        return history

    def _evaluate(self, X_val, y_val):
        preds = self.model.predict(X_val, verbose=0).flatten()
        mse = mean_squared_error(y_val, preds)
        mae = mean_absolute_error(y_val, preds)
        logger.info(f"Validation MSE: {mse:.6f} | MAE: {mae:.6f}")
        return {'mse': mse, 'mae': mae}

    def predict(self, klines):
        if not self.is_trained or self.model is None:
            logger.warning("Model not trained. Returning neutral score.")
            return {'score': 0.0, 'direction': 'NEUTRAL', 'confidence': 0.0}
        try:
            df = self._klines_to_df(klines)
            features = ['open', 'high', 'low', 'close', 'volume', 'returns', 'hl_ratio', 'oc_ratio', 'vol_ma', 'price_ma5', 'price_ma20']
            data = df[features].values
            scaled = self.scaler.transform(data)
            if len(scaled) < self.lookback:
                return {'score': 0.0, 'direction': 'NEUTRAL', 'confidence': 0.0}
            X = scaled[-self.lookback:].reshape(1, self.lookback, scaled.shape[1])
            pred_scaled = self.model.predict(X, verbose=0)[0][0]
            current_scaled = scaled[-1, 3]
            price_change = pred_scaled - current_scaled
            score = float(np.tanh(price_change * 100))
            direction = 'BULLISH' if score > 0 else 'BEARISH'
            return {
                'score': round(score, 4),
                'direction': direction,
                'confidence': round(abs(score), 4),
                'predicted_change_pct': round(price_change * 100, 4)
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {'score': 0.0, 'direction': 'NEUTRAL', 'confidence': 0.0}

    def _try_load_model(self):
        try:
            self.model = load_model(MODEL_SAVE_PATH)
            self.is_trained = True
            logger.info(f"Loaded saved model from {MODEL_SAVE_PATH}")
        except Exception:
            logger.info("No saved model found. Will train from scratch.")

    def save(self):
        if self.model:
            self.model.save(MODEL_SAVE_PATH)
            logger.info(f"Model saved to {MODEL_SAVE_PATH}")
