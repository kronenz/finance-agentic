import enum
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, func
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StrategyType(enum.Enum):
    TREND_FOLLOWING = "TREND_FOLLOWING"
    MEAN_REVERSION = "MEAN_REVERSION"

class TradingStrategy(Base):
    __tablename__ = 'trading_strategies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    strategy_type = Column(Enum(StrategyType), nullable=False)
    description = Column(String, nullable=True)
    parameters = Column(JSON, nullable=False)
    performance_metrics = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    # executed_trades = relationship("Trade", back_populates="strategy")

    @validates('parameters')
    def validate_parameters(self, key, params):
        if not isinstance(params, dict):
            raise ValueError("Parameters must be a JSON object")
        return params

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def __repr__(self):
        return f"<TradingStrategy(id={self.id}, name='{self.name}', active={self.is_active})>"