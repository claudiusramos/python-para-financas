from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)

mt5.initialize()

ativo = "WDO$"

barras = mt5.copy_rates_from(ativo, mt5.TIMEFRAME_D1, datetime.today(), 5000)

# print(barras)

barras_frame = pd.DataFrame(barras)

barras_frame['time'] = pd.to_datetime(barras_frame['time'], unit='s')

print(barras_frame)
mt5.shutdown()

# h5_dados = pd.HDFStore('dados/data.h5', 'r')
#
# data_copy = h5_dados['data']

now = datetime.now()

frame_30Minutos = mt5.TIMEFRAME_M30
frame_1Hora = mt5.TIMEFRAME_H1

def pegaDados(time_frame, asset = "PETR4", year = 2010, month = 1, day = 1):
    mt5.initialize()
    utc_from = datetime(year, month, day)
    utc_to = datetime(now.year, now.month, now.day + 1)
    mt5.symbol_select(asset)
    rates = mt5.copy_rates_range(asset, time_frame, utc_from, utc_to)
    rates_frame = pd.DataFrame(rates)

    return rates_frame
#Coletar de Varios Ativos ao mesmo tempo

df = pegaDados(frame_1Hora)
print(df)