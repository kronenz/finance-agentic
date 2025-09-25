import logging
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional

# This is a placeholder. In a real app, these would be properly managed instances.
from backend.app.trading.execution_engine import TradingExecutionEngine
from backend.app.trading.position_manager import PositionManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()

# Create singleton instances for demonstration purposes
execution_engine = TradingExecutionEngine()
position_manager = PositionManager()


# --- Pydantic Schemas for Request/Response Validation ---

class OrderCreateSchema(BaseModel):
    exchange: str = Field(..., description="Exchange name (e.g., 'binance')")
    symbol: str = Field(..., description="Trading symbol (e.g., 'BTCUSDT')")
    side: str = Field(..., pattern=r"^(buy|sell)$", description="Order side ('buy' or 'sell')")
    quantity: float = Field(..., gt=0, description="Order quantity")
    price: float = Field(..., gt=0, description="Order price")
    order_type: str = Field("LIMIT", description="Order type (e.g., 'LIMIT')")

class OrderCreateResponse(BaseModel):
    order_id: str
    message: str

class OrderStatusResponse(BaseModel):
    id: str
    status: str
    exchange: str
    symbol: str
    executed_price: Optional[float] = None
    quantity: float

class PositionResponse(BaseModel):
    symbol: str
    quantity: float
    average_entry_price: float
    unrealized_pnl: float


# --- API Endpoints ---

@router.post("/orders", response_model=OrderCreateResponse, status_code=202)
async def create_and_execute_order(order: OrderCreateSchema):
    """
    Creates and immediately executes a new trading order.
    """
    try:
        logger.info(f"Received order creation request: {order.dict()}")
        order_id = await execution_engine.create_order(**order.dict())
        # Asynchronously execute the order
        asyncio.create_task(execution_engine.execute_order(order_id))
        return {"order_id": order_id, "message": "Order accepted and is being processed."}
    except ValueError as e:
        logger.error(f"Invalid order data: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.critical(f"Failed to create order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while creating order.")

@router.get("/orders/{order_id}", response_model=OrderStatusResponse)
async def get_order_status(order_id: str):
    """
    Retrieves the status of a specific order.
    """
    logger.info(f"Fetching status for order {order_id}")
    status = execution_engine.get_order_status(order_id)
    if not status:
        logger.warning(f"Order {order_id} not found.")
        raise HTTPException(status_code=404, detail="Order not found.")
    return status

@router.get("/positions/{symbol}", response_model=PositionResponse)
async def get_position(symbol: str):
    """
    Retrieves the current position for a given symbol.
    """
    logger.info(f"Fetching position for symbol {symbol}")
    position = position_manager.get_position(symbol.upper())
    if not position:
        logger.warning(f"No position found for {symbol}.")
        raise HTTPException(status_code=404, detail=f"No position found for symbol {symbol}.")
    return position

# Example of how to integrate this router into a FastAPI app
# In your main.py:
# from fastapi import FastAPI
# from backend.app.api.v1 import trading
#
# app = FastAPI(title="Trading API")
# app.include_router(trading.router, prefix="/api/v1/trading", tags=["Trading"])
#
# @app.on_event("startup")
# async def startup_event():
#     # Start background tasks like the position manager's P&L calculation
#     asyncio.create_task(position_manager.run())
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)