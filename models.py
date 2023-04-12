from pydantic import BaseModel


class LatestStockResponse(BaseModel):
    symbol: str
    price: float


class HistoricalStockResponse(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    date: str
