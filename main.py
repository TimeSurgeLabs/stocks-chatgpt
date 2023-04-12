import io
import os

import arrow
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from dotenv import load_dotenv
import yaml
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, CryptoLatestQuoteRequest, StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

from models import LatestStockResponse, HistoricalStockResponse
from util import resolve_since_time

load_dotenv()

# create a new FastAPI app with cors enabled
app = FastAPI(title="ChatGPT Stocks")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stock_client_hist = StockHistoricalDataClient(
    os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_API_SECRET'))
crypto_client_hist = CryptoHistoricalDataClient(
    os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_API_SECRET'))


@app.get("/")
def index():
    '''Redirect to docs'''
    return RedirectResponse(url="/docs")


@app.get("/stocks/{symbol}", response_model=list[HistoricalStockResponse], description="Gets the the last month of stock prices")
def get_stock_bars(symbol: str):

    req = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=arrow.now().shift(months=-1).datetime,
        end=arrow.now().shift(minutes=-15).datetime,
    )

    resp = stock_client_hist.get_stock_bars(req)
    all_bars = resp[symbol]
    b = []
    for bar in all_bars:
        b.append({
            'symbol': symbol,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'date': arrow.get(bar.timestamp).format('YYYY-MM-DD HH:mm:ss')})
    return b


@app.get("/stocks/{symbol}/{since}", response_model=list[HistoricalStockResponse], description="Gets bars for a stock since a certain time. Second param should be 'day', 'week', 'month', or 'year'")
def get_stock_bars_range(symbol: str, since: str):
    try:
        start, timeframe = resolve_since_time(since)
    except:
        return Response("Invalid since time", status_code=400)

    req = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=timeframe,
        start=start,
        end=arrow.now().shift(minutes=-15).datetime,
    )

    resp = stock_client_hist.get_stock_bars(req)
    all_bars = resp[symbol]
    b = []
    for bar in all_bars:
        b.append({
            'symbol': symbol,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'date': arrow.get(bar.timestamp).format('YYYY-MM-DD HH:mm:ss')})
    return b


@app.get("/cryptos/{symbol}", response_model=list[HistoricalStockResponse], description="Gets the the last month of crypto prices")
def get_crypto_bars(symbol: str):

    resp = crypto_client_hist.get_crypto_bars(
        CryptoBarsRequest(
            symbol_or_symbols=f'{symbol.upper()}/USD',
            timeframe=TimeFrame.Day,
            start=arrow.now().shift(months=-1).datetime,
            end=arrow.now().shift(minutes=-15).datetime,
        ))

    all_bars = resp[f'{symbol.upper()}/USD']
    b = []
    for bar in all_bars:
        b.append({
            'symbol': f'{symbol.upper()}/USD',
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'date': arrow.get(bar.timestamp).format('YYYY-MM-DD HH:mm:ss')})
    return b


@app.get("/cryptos/{symbol}/{since}", response_model=list[HistoricalStockResponse], description="Gets bars for a crypto since a certain time. Second param should be 'day', 'week', 'month', or 'year'")
def get_crypto_bars_range(symbol: str, since: str):
    try:
        start, timeframe = resolve_since_time(since)
    except:
        return Response("Invalid since time", status_code=400)

    resp = crypto_client_hist.get_crypto_bars(
        CryptoBarsRequest(
            symbol_or_symbols=f'{symbol.upper()}/USD',
            timeframe=timeframe,
            start=start,
            end=arrow.now().shift(minutes=-15).datetime,
        ))

    all_bars = resp[f'{symbol.upper()}/USD']
    b = []
    for bar in all_bars:
        b.append({
            'symbol': f'{symbol.upper()}/USD',
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'date': arrow.get(bar.timestamp).format('YYYY-MM-DD HH:mm:ss')})
    return b


@app.get("/stock/{symbol}", response_model=list[HistoricalStockResponse], description="Gets the current stock price")
def get_stock_latest(symbol: str):

    resp = stock_client_hist.get_stock_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol))

    return {
        'symbol': symbol,
        'price': resp[symbol].ask_price
    }


@app.get("/crypto/{symbol}", response_model=LatestStockResponse, description="Gets the current crypto price")
def get_crypto_latest(symbol: str):
    symbol = f'{symbol.upper()}/USD'
    resp = crypto_client_hist.get_crypto_latest_quote(
        CryptoLatestQuoteRequest(symbol_or_symbols=symbol))
    return {
        'symbol': symbol,
        'price': resp[symbol].ask_price
    }


@app.get('/openapi.yaml', include_in_schema=False)
def read_openapi_yaml() -> Response:
    '''Return openapi.yaml'''
    openapi_json = app.openapi()
    yaml_s = io.StringIO()
    yaml.dump(openapi_json, yaml_s)
    return Response(yaml_s.getvalue(), media_type='text/plain')


@app.get('/.well-known/ai-plugin.json', include_in_schema=False)
def read_ai_plugin_json() -> Response:
    with open('ai-plugin.json', 'r') as f:
        return Response(f.read(), media_type='application/json')
