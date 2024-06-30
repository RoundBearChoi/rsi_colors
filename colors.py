import cryptocompare
import matplotlib.pyplot as plt
import numpy as np
import logging
import pandas as pd

from matplotlib.colors import LinearSegmentedColormap
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta


def run():
    print('Hi..')

    today = date.today()
    num_downloads = 3  # Set the number of downloads here
    days_per_download = 1400  # Set the number of days per download here

    print('Downloading ' + str(1400) + ' days worth of data ' + str(num_downloads) + ' times..')
    total_days = num_downloads * days_per_download
    print('Total of ' + str(total_days) + ' days..')
    total_years = round(total_days / 365, 2)
    print(str(total_years) + ' years..')

    data = []

    for i in range(num_downloads):
        download_date = today - timedelta(days=i*days_per_download)
        data_part = cryptocompare.get_historical_price_day('BTC', currency='USD', limit=2000, toTs=download_date)
        data += data_part

    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True, drop=False)
    df = df.resample('ME').last().asfreq('ME')

    # Calculate the RSI
    delta = df['close'].diff()
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up/ema_down

    df['RSI'] = 100 - (100/(1 + rs))

    plt.style.use('dark_background')
    plt.figure(figsize=(14, 7))
    plt.title('Monthly RSI')

    log_data(df)
    plot_rsi(df)

    plt.show()


def plot_rsi(df):
    plot_logger = logging.getLogger('plot_logger')
    plot_logger.setLevel(logging.INFO)
    plot_handler = logging.FileHandler('plot.log', mode='w')
    plot_logger.addHandler(plot_handler)

    # 2028-04-17 is next predicted date
    halving_dates = ['2012-11-28', '2016-07-09', '2020-05-11', '2024-04-19', '2028-04-17']
    halving_dates = pd.to_datetime(halving_dates)
    halving_dates = pd.DatetimeIndex(halving_dates)

    norm = plt.Normalize(0, 50)

    for i in np.arange(1, len(df)):
        x_values = df.index[i - 1:i + 1]
        y_values = df['RSI'][i - 1:i + 1]

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


def log_data(df):
    data_logger = logging.getLogger('data_logger')
    data_logger.setLevel(logging.INFO)
    data_handler = logging.FileHandler('data.log', mode='w')
    data_logger.addHandler(data_handler)

    data_logger.info(df)


if __name__ == '__main__':
    run()
