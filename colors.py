import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import logging
import pandas as pd

from matplotlib.colors import LinearSegmentedColormap
from dateutil.relativedelta import relativedelta
from datetime import date


def run():
    print('Hi..')

    today = date.today()
    data = yf.download('BTC-USD', start='2015-01-01', end=today)
    print("Today's date: " + str(today))
    monthly_data = data.resample('ME').last().asfreq('ME')

    # Calculate the RSI
    delta = monthly_data['Close'].diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up/ema_down

    monthly_data['RSI'] = 100 - (100/(1 + rs))

    plt.style.use('dark_background')
    plt.figure(figsize=(14, 7))
    plt.title('Monthly RSI')

    log_data(monthly_data)
    plot_rsi(monthly_data)

    plt.show()


def plot_rsi(monthly_data):
    plot_logger = logging.getLogger('plot_logger')
    plot_logger.setLevel(logging.INFO)
    plot_handler = logging.FileHandler('plot.log', mode='w')
    plot_logger.addHandler(plot_handler)

    # 2028-04-17 is next predicted date
    halving_dates = ['2012-11-28', '2016-07-09', '2020-05-11', '2024-04-19', '2028-04-17']
    halving_dates = pd.to_datetime(halving_dates)
    halving_dates = pd.DatetimeIndex(halving_dates)

    norm = plt.Normalize(0, 50)

    for i in np.arange(1, len(monthly_data)):
        x_values = monthly_data.index[i - 1:i + 1]
        y_values = monthly_data['RSI'][i - 1:i + 1]

        months_left = None

        for halving_date in halving_dates:
            if x_values[1] < halving_date:
                diff = relativedelta(halving_date, x_values[0])
                months_left = diff.years * 12 + diff.months
                break

        cmap = LinearSegmentedColormap.from_list('my_cmap', ['lightgreen', 'red'])
        color_value = cmap(norm(months_left))

        plt.plot(x_values, y_values, color=color_value)

        plot_logger.info(
            f'x_values: {x_values},'
            f' y_values: {y_values},'
            f' color_value: {color_value},'
            f' months_left: {months_left}')
        plot_logger.info('')


def log_data(monthly_data):
    data_logger = logging.getLogger('data_logger')
    data_logger.setLevel(logging.INFO)
    data_handler = logging.FileHandler('data.log', mode='w')
    data_logger.addHandler(data_handler)

    data_logger.info(monthly_data)


if __name__ == '__main__':
    run()
