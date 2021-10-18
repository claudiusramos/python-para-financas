import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import time
import talib
import random
import numpy as np

#configura parâmetros da biblioteca pandas
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)
pd.set_option('mode.chained_assignment', None)

#define o ativo
ativo = 'WINJ21'
mt5.initialize()
mt5.symbol_select(ativo)

stop_loss = 500
take_profit = 500

def ordem_fechamento(ativo, quantidade, ticket, type_order, magic, deviation):
    if(type_order == 0):
        print("ORDEM DE VENDA - FECHAMENTO")
        request_fechamento = {
            "action": mt5.TRADE_ACTION_DEAL,
            "postion": ticket,
            "symbol": ativo,
            "volume": quantidade,
            "deviation": deviation,
            "magic": magic,
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(ativo).bid,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN
        }

        resultado = mt5.order_send(request_fechamento)
        print(resultado)
    else:
        print("ORDEM DE COMPRA - FECHAMENTO")
        request_fechamento = {
            "action": mt5.TRADE_ACTION_DEAL,
            "postion": ticket,
            "symbol": ativo,
            "volume": quantidade,
            "deviation": deviation,
            "magic": magic,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(ativo).ask,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN
        }

        resultado = mt5.order_send(request_fechamento)
        print(resultado)

def venda():
    print("ORDEM DE VENDA ENVIADA")
    lot = float(1)
    symbol = ativo
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).last
    deviation = 5
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
    deviation = 5
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

df = pd.DataFrame()
df = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_M1, 1, 5000)
df = pd.DataFrame(df)
df['time'] = pd.to_datetime(df['time'], unit = 's')
df = df.set_index('time') #tempo em index

df['ema9'] = talib.EMA(df['close'].values, timeperiod  = 9)
df['ema21'] = talib.EMA(df['close'].values, timeperiod = 21)

while True:

    total_ordens = mt5.positions_total()
    dr = pd.DataFrame()
    dr = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_M1, 0, 1)
    dr = pd.DataFrame(dr)
    dr['time'] = pd.to_datetime(dr['time'], unit='s')
    dr = dr.set_index('time')  # tempo em index
    df = df.append(dr)
    df['ema9'] = talib.EMA(df['close'].values, timeperiod=9)
    df['ema21'] = talib.EMA(df['close'].values, timeperiod=21)
    df['signal'] = np.sign(df['ema9'] - df['ema21'])
    print(df)

    if(total_ordens == 0):
        if(df['signal'].iloc[-1] == 1):
            print(compra())
            total_ordens = mt5.positions_total()
        else:
            print(venda())
            total_ordens = mt5.positions_total()
    elif(total_ordens == 1):
        info_posicoes = mt5.positions_get(symbol= ativo)
        data_posicoes = pd.DataFrame(list(info_posicoes), columns=info_posicoes[0]._asdict().keys())

        if(data_posicoes['type'][0] == 0 and df['signal'].iloc[-1] == -1):
            print(ordem_fechamento(str(data_posicoes['symbol'][0]),
                                   float(data_posicoes['volume'][0]),
                                   int(data_posicoes['ticket'][0]),
                                   data_posicoes['type'][0],
                                   int(data_posicoes['magic'][0]),
                                   0))
            print(venda())

        if(data_posicoes['type'][0] == 1 and df['signal'].iloc[-1] == 1):
            print(ordem_fechamento(str(data_posicoes['symbol'][0]),
                                   float(data_posicoes['volume'][0]),
                                   int(data_posicoes['ticket'][0]),
                                   data_posicoes['type'][0],
                                   int(data_posicoes['magic'][0]),
                                   0))
            print(compra())

    time.sleep(60)