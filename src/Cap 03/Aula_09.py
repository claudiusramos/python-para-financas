from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
from pylab import mpl, plt
import numpy as np

#configura os parâmetros para plotagem do gráfico
plt.style.use('seaborn')
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.family'] = 'serif'

#configura parâmetros da biblioteca pandas
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)
pd.set_option('mode.chained_assignment', None)

mt5.initialize()

ativo = "BOVA11"

barras = mt5.copy_rates_from(ativo, mt5.TIMEFRAME_D1, datetime.today(), 5000)

# print(barras)

data = pd.DataFrame(barras)

data['time'] = pd.to_datetime(data['time'], unit='s')

# print(data)

data['SMACURTA'] = data['close'].rolling(43).mean()
data['SMALONGA'] = data['close'].rolling(252).mean()

data.dropna(inplace= True)

data = data[['time', 'close', 'SMACURTA', 'SMALONGA']]

data = data.set_index('time')

data.plot(title = "Média de 43 e 252 do Ativo: " + ativo, figsize = (20,12))

# plt.show()

data['posicao'] = np.where(data['SMACURTA'] > data['SMALONGA'], 1, -1)

data['posicao'] = data['posicao'].shift(1)
data.dropna(inplace=True)

data.plot(figsize = (20,12), secondary_y = 'posicao')
# plt.show()

data['retornos'] = np.log(data['close']/data['close'].shift(1))
data.dropna(inplace= True)

data['estrategia'] = data['posicao'] * data['retornos']

retorno_simples = data[['retornos', 'estrategia']].sum()
retorno_log = data[['retornos', 'estrategia']].sum().apply(np.exp) - 1

print(retorno_simples)
print(retorno_log)

data[['retornos', 'estrategia']].cumsum().apply(np.exp).plot(figsize = (20,12))

plt.show()

data['retornoacumulado'] = data['estrategia'].cumsum().apply(np.exp)
data['somamaxima'] = data['retornoacumulado'].cummax()

data[['retornoacumulado', 'somamaxima']].dropna().plot(figsize = (20,12))
plt.show()

drawdown = data['somamaxima'] - data['retornoacumulado']

rebaixamento = drawdown.max()

print('Rebaixamento: ' + str(rebaixamento))

temp = drawdown[drawdown == 0]

print(temp)

periodos = (temp.index[1:].to_pydatetime() - temp.index[:-1].to_pydatetime())
print(periodos.max())