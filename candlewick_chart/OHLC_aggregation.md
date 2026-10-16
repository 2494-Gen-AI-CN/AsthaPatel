## OHLC aggregation
- Objective: use OHLC aggregation to create buckets of various tiemframes to reveal underlying trends in the share prices

## implementation
- Pandas to use its built-in functions to load the csv file data, resample, and aggregate the candles into selected timeframe
- streamlit handles the user interface by mimicing a traditional trading platform site
- Plotly is utilized to implement the graphical UI by including horizontal and vertical zoom features, as well as adding a scrollable backfill to the plot.
- Python is used to implement the functions that combine all of the above components together.
    - ohlc_agg(data, tiemframe): returns a dataframe that repsenta rows populated based on the timeframe selected

## start command
- py -3.15 -m streamlit run OHLC_aggregation.py