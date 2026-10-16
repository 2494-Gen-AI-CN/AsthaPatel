## OHLC aggregation

### Objective
- Build a Python applciation that converts NAS100 (NDX) stock tick level data to build a candlewick chart for chosen timeframe (1m, 30 min, 1 hr).
- Each candle wick body represents the open and close level within that specific timeframe

### Techstack
- Python to build the application
- pandas for aggregation
- matplotlib for drawing candles
- Tkinter for interactive navigation (selecting timeframes)

### Data format (symbol: NAS100)
- Format: Date (MM/DD/YYYY), timestamp (HH:MM:SS), open price (USD), close price (USD), high price (USD), low price (USD)
- the data rows are populated with 1-minute candle wick data

### Start command
- py OHLC_aggregation.py