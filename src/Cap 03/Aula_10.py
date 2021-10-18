from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import matplotlib
from matplotlib.pylab import mpl, plt
import numpy as np
import backtrader as bt

#configura os parâmetros para plotagem do gráfico
plt.style.use('seaborn')
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.family'] = 'serif'

#configura parâmetros da biblioteca pandas
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)
pd.set_option('mode.chained_assignment', None)

mt5.initialize()

ativo = "VALE3"

barras = mt5.copy_rates_from(ativo, mt5.TIMEFRAME_D1, datetime.today(), 5000)

# print(barras)

data = pd.DataFrame(barras)

data['time'] = pd.to_datetime(data['time'], unit='s')

data_signal = pd.DataFrame(index = data.index)
data_signal['price'] = data['close']

data_signal['diferenca_diaria'] = data_signal['price'].diff()
data_signal['sinal'] = 0.0

#codigo de compra = 0 - Compro quando a diff <= 0
#codigo de venda = 1 - Vendo quando a diff > 0

data_signal['sinal'] = np.where(data_signal['diferenca_diaria'] > 0, 1.0, 0.0)

data_signal['positions'] = data_signal['sinal'].diff()

capital_inicial = 10000

positions = pd.DataFrame(index = data_signal.index).fillna(0.0)
portfolio = pd.DataFrame(index = data_signal.index).fillna(0.0)

positions['BOVA11'] = data_signal['sinal']
portfolio['positions'] = (positions.multiply(data_signal['price'], axis = 0)).cumsum()

portfolio['cash'] = capital_inicial - (positions.diff().multiply(data_signal['price'], axis = 0)).cumsum()

portfolio['total'] = portfolio['positions'] + portfolio['cash']

print(portfolio)

mt5.shutdown()