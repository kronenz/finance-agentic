from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()

class VolumeProfile(Base):
    __tablename__ = 'volume_profiles'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    
    poc_price = Column(Float, nullable=False)  # Point of Control
    vah_price = Column(Float, nullable=False)  # Value Area High
    val_price = Column(Float, nullable=False)  # Value Area Low
    
    # Low Volume Nodes (LVNs) stored as an array of floats
    lvn_zones = Column(ARRAY(Float), nullable=True)

    @hybrid_property
    def value_area(self):
        """Represents the market consensus area."""
        return (self.val_price, self.vah_price)

    def is_price_in_value_area(self, price: float) -> bool:
        """Checks if a given price is within the value area."""
        return self.val_price <= price <= self.vah_price

    def __repr__(self):
        return f"<VolumeProfile(symbol='{self.symbol}', poc={self.poc_price})>"