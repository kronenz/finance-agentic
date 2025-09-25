import enum
from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, func, DateTime
from sqlalchemy.orm import relationship, validates, declarative_base

Base = declarative_base()

class RiskLevel(enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    PORTFOLIO = "PORTFOLIO"
    SYSTEM = "SYSTEM"

class RiskParameters(Base):
    __tablename__ = 'risk_parameters'

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Enum(RiskLevel), nullable=False)
    name = Column(String, nullable=False) # e.g., 'BTC/USDT', 'Main Portfolio', 'Global'
    
    # Core risk parameters
    max_position_size = Column(Float, nullable=True)
    max_daily_loss = Column(Float, nullable=True)
    leverage_limit = Column(Float, default=1.0)
    
    # Parameters for monitoring cascading liquidation risk
    liquidation_threshold = Column(Float, nullable=True) # e.g., margin level at which liquidation is triggered
    max_exposure_concentration = Column(Float, nullable=True) # Max % of portfolio in a single asset

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Example of a relationship if linking to a specific portfolio or user
    # portfolio_id = Column(Integer, ForeignKey('portfolios.id'))
    # portfolio = relationship("Portfolio", back_populates="risk_params")

    @validates('leverage_limit', 'max_daily_loss')
    def validate_positive_values(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} cannot be negative.")
        return value

    def __repr__(self):
        return f"<RiskParameters(level='{self.level.value}', name='{self.name}')>"