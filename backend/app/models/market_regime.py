import enum
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, func
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MarketRegimeType(enum.Enum):
    TREND_UP = "TREND_UP"
    TREND_DOWN = "TREND_DOWN"
    RANGE_HIGH_VOL = "RANGE_HIGH_VOL"
    RANGE_LOW_VOL = "RANGE_LOW_VOL"
    CRASH_EVENT = "CRASH_EVENT"

class MarketRegime(Base):
    __tablename__ = 'market_regimes'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    regime_type = Column(Enum(MarketRegimeType), nullable=False)
    confidence_score = Column(Float, nullable=False)
    adx_value = Column(Float, nullable=True)
    hurst_exponent = Column(Float, nullable=True)
    volatility_level = Column(Float, nullable=True)

    # Relationships
    # Assuming a relationship to trading signals or strategies
    # trading_signals = relationship("TradingSignal", back_populates="market_regime")

    @validates('confidence_score')
    def validate_confidence_score(self, key, score):
        if not 0.0 <= score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return score

    def __repr__(self):
        return f"<MarketRegime(id={self.id}, regime='{self.regime_type.value}', confidence={self.confidence_score})>"