# To differentiate between time-time and datetime-time
import time as true_time
import pprint
import pathlib
import operator
import pandas as pd

from datetime import datetime
from datetime import timedelta
from configparser import ConfigParser

from bot.bot import Bot
from bot.indicators import Indicators

# Grab the config file values.
config = ConfigParser()
config.read('configs/config.ini')

CLIENT_ID = config.get('main', 'CLIENT_ID')
REDIRECT_URI = config.get('main', 'REDIRECT_URI')
CREDENTIALS_PATH = config.get('main', 'JSON_PATH')
ACCOUNT_NUMBER = config.get('main', 'ACCOUNT_NUMBER')

# Initialize the robot.
trading_robot = Bot(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    crendentials_path=CREDENTIALS_PATH,
    trading_account=ACCOUNT_NUMBER,
    paper_trading=True
)

# Create a new portfolio.
trading_robot_portfolio = trading_robot.create_portfolio()

# Add multiple positions to our portfolio.
multi_position = [
    {
        'asset_type': 'equity',
        'quantity': 2,
        'purchase_price': 4.00,
        'symbol': 'TSLA',
        'purchase_date': '2021-01-06'
    },
    {
        'asset_type': 'equity',
        'quantity': 2,
        'purchase_price': 4.00,
        'symbol': 'SQ',
        'purchase_date': '2021-01-06'
    }
]

# Add those positions to the Portfolio.
new_positions = trading_robot.portfolio.add_positions(positions=multi_position)

# Add a single position to the portfolio.
trading_robot.portfolio.add_position(
    symbol='MSFT',
    quantity=10,
    purchase_price=10.00,
    asset_type='equity',
    purchase_date='2021-01-08'
)
pprint.pprint(trading_robot.portfolio.positions)

# Check to see if regular market is open.
if trading_robot.regular_market_open:
    print('Regular Market Open')
else:
    print('Regular Market Not Open')

# Check to see if Pre market is open.
if trading_robot.pre_market_open:
    print('Pre Market Open')
else:
    print('Pre Market Not Open')

# Check to see if Post market is open.
if trading_robot.post_market_open:
    print('Post Market Open')
else:
    print('Post Market Not Open')

# Grab the current quotes in our portfolio.
current_quotes = trading_robot.grab_current_quotes()
pprint.pprint(current_quotes)

# Define our date range.
end_date = datetime.today()
start_date = end_date - timedelta(days=30)

# Grab the historical prices.
historical_prices = trading_robot.grab_historical_prices(
    start=start_date,
    end=end_date,
    bar_size=1,
    bar_type='minute'
)

# Convert the data into a StockFrame.
stock_frame = trading_robot.create_stock_frame(data=historical_prices['aggregated'])

# Print the head of the StockFrame.
pprint.pprint(stock_frame.frame.head(20))