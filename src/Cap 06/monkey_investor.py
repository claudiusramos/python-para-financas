import time
import random
import MetaTrader5 as mt5
import pandas as pd

#opcoes do pandas
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)
pd.set_option('mode.chained_assignment', None)

mt5.initialize()

ativo = 'WINJ21'

selecionado = mt5.symbol_select(ativo)
info_posicoes = mt5.positions_get(symbol=ativo)
total_ordens = mt5.positions_total()

#Coleta Dados do Ativo
# df = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_M15, 0, 5000)
# df = pd.DataFrame(df)
# df['time'] = pd.to_datetime(df['time'], unit = 's')
# df = df.set_index('time') #tempo em index
# df['diff_hl'] = df['high'] - df['low']
#
# print(df['diff_hl'].describe())

stop_loss = 500
take_profit = 500

tipo_de_ordem = [0 , 1]

def venda():
    print("ORDEM DE VENDA ENVIADA")
    lot = float(1)
    symbol = ativo
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).last
    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price + stop_loss * point,
        "tp": price - take_profit * point,
        "deviation": deviation,
        "magic": 10032021,
        "comment": "Ordem de Venda Enviada",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN
    }
    resultado = mt5.order_send(request)
    return resultado

def compra():
    print("ORDEM DE COMPRA ENVIADA")
    lot = float(1)
    symbol = ativo
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).last
    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price - stop_loss * point,
        "tp": price + take_profit * point,
        "deviation": deviation,
        "magic": 10032021,
        "comment": "Ordem de Compra Enviada",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN
    }
    resultado = mt5.order_send(request)
    return resultado

while True:
    if total_ordens <= 5:
        print('Total de Ordens: ' + str(total_ordens))
        escolha = random.choice(tipo_de_ordem)
        if escolha == 0:
            print(compra())
        else:
            print(venda())
    else:
        print('Nada a Fazer por Enquanto')
    total_ordens = mt5.positions_total()
    time.sleep(15*60)

mt5.shutdown()