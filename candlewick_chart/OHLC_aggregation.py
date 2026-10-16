import pandas as pd
import matplotlib

# 1. Load the csv file into a pandas DataFrame 
# Data is a 5-day OHLC data for NAS100 index for October 2026.
df = pd.read_csv('NAS100_5D_2026_data.csv')

# set 'date' as index and sort in ascending order for proper resampling
df = df.set_index("date").sort_index() 

# define timeframes
TIMEFRAMES = {
    "1m" : "1min",
    "30m" : "30min",
    "1h" : "1h",
    "4h" : "4h",
    "1d" : "1d"
}
# 2. OHLC aggregation
def ohlc_agg(data, timeframe):
    # define the aggregation functions for each column
    agg_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }

    # resample() traverses through the data and groups it into the specified timeframe
    # agg() applies the aggregation functions defined in agg_dict to each group
    return data.resample(timeframe).agg(agg_dict)

# 3. get candles for specific day to avoid
def get_day_candles(data, selected_date, timeframe):
    # results in a brand new dataframe with only the selected date's data
    day_data = data.loc[data.index.date == selected_date] 
    return ohlc_agg(day_data, timeframe)
