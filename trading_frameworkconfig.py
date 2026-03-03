"""
Configuration module for the Autonomous Adaptive Trading Framework.
Centralized configuration with Firebase integration for runtime updates.
"""
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

class TradingMode(Enum):
    """Operational modes for the trading framework."""
    BACKTEST = "backtest"
    PAPER = "paper_trading"
    LIVE = "live_trading"
    RESEARCH = "strategy_research"

class ExchangeType(Enum):
    """Supported cryptocurrency exchanges."""
    BINANCE = "binance"
    COINBASE = "coinbase"
    KRAKEN = "kraken"

@dataclass
class TradingConfig:
    """Main configuration class with sensible defaults."""
    # Firebase Configuration
    firebase_credentials_path: str = field(
        default_factory=lambda: os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
    )
    
    # Trading Parameters
    mode: TradingMode = TradingMode.PAPER
    exchange: ExchangeType = ExchangeType.BINANCE
    trading_pairs: List[str] = field(default_factory=lambda: ["BTC/USDT", "ETH/USDT"])
    timeframe: str = "1h"
    initial_capital: float = 10000.0
    
    # RL Training Parameters
    learning_rate: float = 0.001
    discount_factor: float = 0.95
    exploration_rate: float = 0.1
    batch_size: int = 32
    memory_size: int = 10000
    training_episodes: int = 1000
    
    # Neural Network Architecture
    hidden_layers: List[int] = field(default_factory=lambda: [128, 64, 32])
    dropout_rate: float = 0.2
    activation: str = "relu"
    
    # Risk Management
    max_position_size: float = 0.1  # 10% of portfolio
    stop_loss_pct: float = 0.02    # 2%
    take_profit_pct: float = 0.05  # 5%
    max_daily_loss: float = 0.03   # 3%
    
    # System Parameters
    data_buffer_size: int = 1000
    checkpoint_interval: int = 100  # episodes
    log_level: str = "INFO"
    
    # Performance Tracking
    performance_metrics: List[str] = field(default_factory=lambda: [
        "sharpe_ratio", "max_drawdown", "win_rate", "profit_factor"
    ])
    
    def __post_init__(self):
        """Initialize Firebase if credentials exist."""
        self._init_firebase()
        self._validate_config()
    
    def _init_firebase(self):
        """Initialize Firebase connection for real-time configuration."""
        try:
            if os.path.exists(self.firebase_credentials_path):
                cred = credentials.Certificate(self.firebase_credentials_path)
                firebase_admin.initialize_app(cred)
                self.firestore_client = firestore.client()
                print("✅ Firebase initialized successfully")
            else:
                print("⚠️ Firebase credentials not found. Running in local mode.")
                self.firestore_client = None
        except Exception as e:
            print(f"⚠️ Firebase initialization failed: {e}")
            self.firestore_client = None
    
    def _validate_config(self):
        """Validate configuration parameters."""
        if self.initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        if not 0 <= self.exploration_rate <= 1:
            raise ValueError("Exploration rate must be between 0 and 1")
        if not 0 <= self.stop_loss_pct <= 1:
            raise ValueError("Stop loss percentage must be between 0 and 1")

# Global configuration instance
config = TradingConfig()

def update_config