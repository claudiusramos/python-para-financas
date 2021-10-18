import MetaTrader5 as mt5
from datetime import datetime
import time
import pandas as pd
import numpy as np

#configura parâmetros da biblioteca pandas
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)
pd.set_option('mode.chained_assignment', None)

horario_inicio_mercado = pd.Timestamp(datetime.today().strftime("%Y-%m-%d") + "-10:00:00")
horario_fechamento_mercado = pd.Timestamp(datetime.today().strftime("%Y-%m-%d") + "-17:50:00")

ativo = "WINJ21"

mt5.initialize()

selecionado = mt5.symbol_select(ativo)
ultimo_preco = mt5.symbol_info_tick(ativo).last

stop_loss = 500
take_profit = 500

def ordem_fechamento(ativo, quantidade, ticket, type_order, magic, deviation):

    if(type_order == 0):
        point = mt5.symbol_info(ativo).point
        price = mt5.symbol_info_tick(ativo).last
        print("ORDEM DE VENDA - FECHAMENTO")
        request_fechamento = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
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

    elif(type_order == 1):
        point = mt5.symbol_info(ativo).point
        price = mt5.symbol_info_tick(ativo).last
        print("ORDEM DE COMPRA - FECHAMENTO")
        request_fechamento = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
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

def ordem_compra(ativo, quantidade):
    print("ORDEM DE COMPRA ENVIADA")
    lot = float(quantidade)
    symbol = ativo
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).last
    price = mt5.symbol_info_tick(symbol).last
    deviation = 0

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price - stop_loss *point,
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
    hora_agora = datetime.now()
    to_dentro_horario = hora_agora >= horario_inicio_mercado and hora_agora <= horario_fechamento_mercado
    ordens_abertas = mt5.orders_total()
    posicoes_abertas = mt5.positions_total()
    print("Ordens Abertas: " + str(ordens_abertas))
    print("Posicoes Abertas: " + str(posicoes_abertas))

    if (posicoes_abertas == 0):
        print(ordem_compra(ativo, 1))
        time.sleep(5)
    else:
        info_posicoes = mt5.positions_get(symbol=ativo)
        if (len(info_posicoes) > 0):
            df = pd.DataFrame(list(info_posicoes), columns=info_posicoes[0]._asdict().keys())
            df['time'] = pd.to_datetime(df['time'], unit='s')
            ordem_fechamento(str(df['symbol'][0]),
                             float(df['volume'][0]),
                             int(df['ticket'][0]),
                             df['type'][0],
                             int(df['magic'][0]),
                             0)
        time.sleep(5)