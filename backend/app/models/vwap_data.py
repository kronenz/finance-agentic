from sqlalchemy import Column, Integer, String, Float, DateTime, Index, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class VWAPData(Base):
    __tablename__ = 'vwap_data'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    vwap_value = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # Using regular columns for deviation bands for simplicity.
    # In a real-world scenario, this might be calculated on the fly or stored separately.
    # This example assumes a simple +/- 2% deviation band.
    deviation_upper_band = Column(Float, nullable=True)
    deviation_lower_band = Column(Float, nullable=True)

    __table_args__ = (
        Index('ix_vwap_data_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
    )

    def __repr__(self):
        return f"<VWAPData(symbol='{self.symbol}', timeframe='{self.timeframe}', vwap={self.vwap_value})>"