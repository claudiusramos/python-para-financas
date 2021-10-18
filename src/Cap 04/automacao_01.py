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

ativo = "PETR4F"

mt5.initialize()
account = mt5.account_info()
assert account.margin_mode == mt5.ACCOUNT_MARGIN_MODE_RETAIL_HEDGING
selecionado = mt5.symbol_select(ativo)
ultimo_preco = mt5.symbol_info_tick(ativo).last


def ordem_compra(ativo, quantidade):
    print("ORDEM DE COMPRA ENVIADA")
    lot = float(quantidade)
    symbol = ativo
    price = mt5.symbol_info_tick(symbol).last
    deviation = 0

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price * 0.95,
        "tp": price * 1.05,
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

    if(ordens_abertas == 0 and posicoes_abertas == 0):
        print(ordem_compra(ativo, 1))
    else:
        info_posicoes = mt5.positions_get(symbol=ativo)
        if(len(info_posicoes) > 0):
            df = pd.DataFrame(list(info_posicoes), columns= info_posicoes[0]._asdict().keys())
            df['time'] = pd.to_datetime(df['time'], unit='s')
            print(df)
            print("Ticket: " + str(df['ticket'][0]))
            print("Magic: " + str(df['magic'][0]))

            time.sleep(2)

