import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import time
import talib
import numpy as np

mt5.initialize()

def VerificaHorarioOperacoes():
    # print('retorna o horario')
    horario_inicio_mercado = pd.Timestamp(datetime.today().strftime("%Y-%m-%d") + "-09:30:00")
    horario_meio_mercado = pd.Timestamp(datetime.today().strftime("%Y-%m-%d") + "-12:00:00")
    horario_tarde_mercado = pd.Timestamp(datetime.today().strftime("%Y-%m-%d") + "-15:30:00")
    horario_fechamento_mercado = pd.Timestamp(datetime.today().strftime("%Y-%m-%d") + "-17:30:00")

    hora_agora = datetime.now()

    if(hora_agora >= horario_inicio_mercado and hora_agora <= horario_meio_mercado) or (hora_agora >= horario_tarde_mercado and hora_agora <= horario_fechamento_mercado):
        return True
    else:
        return False

def ColetaValorDisponivel():
    # print('retorna a margem')
    account_info = mt5.account_info()
    account_info_dict = mt5.account_info()._asdict()
    df = pd.DataFrame(list(account_info_dict.items()), columns=['property', 'value'])
    balance = df['value'][10]

    return balance

def VerificaTemOperacao():
    # print('retorna se tem Operacao')
    total_ordens = mt5.positions_total()
    if total_ordens > 0:
        return True
    else:
        return False

def ordem_fechamento(ativo, quantidade, ticket, type_order, magic, deviation):
    if(type_order == 0):
        print("ORDEM DE VENDA - FECHAMENTO")
        request_fechamento = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": ativo,
            "volume": quantidade,
            "deviation": deviation,
            "magic": magic,
            "type": mt5.ORDER_TYPE_SELL,
            "price": mt5.symbol_info_tick(ativo).ask,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN
        }

        resultado = mt5.order_send(request_fechamento)
        print(resultado)
    else:
        print("ORDEM DE COMPRA - FECHAMENTO")
        request_fechamento = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": ativo,
            "volume": quantidade,
            "deviation": deviation,
            "magic": magic,
            "type": mt5.ORDER_TYPE_BUY,
            "price": mt5.symbol_info_tick(ativo).bid,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN
        }

        resultado = mt5.order_send(request_fechamento)
        print(resultado)

def venda(quantidade):
    print("ORDEM DE VENDA ENVIADA")
    lot = float(1)
    symbol = ativo
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).last
    deviation = 5
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": quantidade,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": price + stop_loss * point,
        "tp": price - take_profit * point,
        "deviation": deviation,
        "magic": 23121987,
        "comment": "Ordem de Venda Enviada",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN
    }
    resultado = mt5.order_send(request)
    return resultado

def compra(quantidade):
    print("ORDEM DE COMPRA ENVIADA")
    lot = float(1)
    symbol = ativo
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).last
    deviation = 5
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": quantidade,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price - stop_loss * point,
        "tp": price + take_profit * point,
        "deviation": deviation,
        "magic": 23121987,
        "comment": "Ordem de Compra Enviada",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN
    }
    resultado = mt5.order_send(request)
    return resultado


#configurar parâmetros da biblioteca pandas
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)

#Determina o Horário de Início das Operações
media_curta = 9
media_longa = 21

ativo = "WINM21"
selecionado= mt5.symbol_select(ativo)
stop_loss = 1000
stop_loss_movel = 0
take_profit = 500
gatilho = 50
gap = 10
qt_contratos = float(1)

while True:
    time.sleep(1)
    if VerificaHorarioOperacoes() and ColetaValorDisponivel() > 50:
        total_ordens = mt5.positions_total()
        # Puxa os dados
        df = pd.DataFrame()
        df = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_M1, 1, 50)
        df = pd.DataFrame(df)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df.set_index('time')
        # Data Frame auxiliar
        dr = pd.DataFrame()
        dr = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_M1, 0, 1)
        dr = pd.DataFrame(dr)
        dr['time'] = pd.to_datetime(dr['time'], unit='s')
        dr = dr.set_index('time')
        df = df.append(dr)
        # Defino os indicadores e condicionais
        df['media_curta'] = talib.EMA(df['close'].values, timeperiod=media_curta)
        df['media_longa'] = talib.EMA(df['close'].values, timeperiod=media_longa)
        df['signal'] = np.sign(df['media_curta'] - df['media_longa'])
        df['diff'] = df['media_curta'] - df['media_longa']


        precoAtual = df['close'].iloc[-1]


        # Imprime o que tá acontecendo
        print('\n' + '=' * 50)
        print('NOVO SINAL | {}'.format(datetime.now()))
        print('=' * 50)
        print(df.iloc[-1].tail(8))



        if (total_ordens == 0):
            print('0 ordens')
            # Determino as condicoes de compra
            if (np.abs(df['diff'].iloc[-1]) <= gatilho and np.abs(df['diff'].iloc[-1]) >= gap and df['media_curta'].iloc[-1] >
                    df['media_longa'].iloc[-1] and df['close'].iloc[-1] > df['media_longa'].iloc[-1] and df['signal'].iloc[
                        -1] == 1):
                # se a diferenca for menor do que o gatilho
                # se a diferenca for maior do que o gap
                # se a media menor esta acima da media maior
                # se o valor atual está acima da média maior
                # se o sinal é de compra
                print(compra(qt_contratos))
            elif (np.abs(df['diff'].iloc[-1]) <= gatilho and np.abs(df['diff'].iloc[-1]) >= gap and df['media_curta'].iloc[
                -1] < df['media_longa'].iloc[-1] and df['close'].iloc[-1] < df['media_longa'].iloc[-1] and df['signal'].iloc[
                      -1] == -1):
                # se a diferenca for menor do que o gatilho
                # se a diferenca for maior do que o gap
                # se a media menor esta abaixo da media maior
                # se o valor atual está abaixo da média maior
                # se o sinal é de venda
                print(venda(qt_contratos))
            else:
                print('NAO FAZ NADA')

            # Se existe uma ordem
        elif (total_ordens == 1):

            info_posicoes = mt5.positions_get(symbol= ativo)
            data_posicoes = pd.DataFrame(list(info_posicoes), columns = info_posicoes[0]._asdict().keys())

            # define o stop_loss
            if (data_posicoes['type'][0] == 0):
                # stop_loss_movel = df['low'].iloc[-3]
                stop_loss_movel = df['media_longa'].iloc[-1] - gatilho
            else:
                # stop_loss_movel = df['high'].iloc[-3]
                stop_loss_movel = df['media_longa'].iloc[-1] + gatilho

            # if (data_posicoes['type'][0] == 0 and (df['signal'].iloc[-1] == -1 or df['close'].iloc[-1] <= stop_loss_movel)):
            if (data_posicoes['type'][0] == 0 and (df['close'].iloc[-1] <= stop_loss_movel)):
                print(ordem_fechamento(str(data_posicoes['symbol'][0]),
                                       float(data_posicoes['volume'][0]),
                                       int(data_posicoes['ticket'][0]),
                                       data_posicoes['type'][0],
                                       int(data_posicoes['magic'][0]),
                                       0))

                # print(venda())
                # print('venda')
                total_ordens = 0
                time.sleep(1)

            # if (data_posicoes['type'][0] == 1 and (df['signal'].iloc[-1] == 1 or df['close'].iloc[-1] >= stop_loss_movel)):
            if (data_posicoes['type'][0] == 1 and (df['close'].iloc[-1] >= stop_loss_movel)):
                print(ordem_fechamento(str(data_posicoes['symbol'][0]),
                                       float(data_posicoes['volume'][0]),
                                       int(data_posicoes['ticket'][0]),
                                       data_posicoes['type'][0],
                                       int(data_posicoes['magic'][0]),
                                       0))
                # print(compra())
                # print('compra')
                total_ordens = 0
                time.sleep(1)
        else:
            print('DOING NOTHING')

        print('STOP LOSS MOVEL: ' + str(stop_loss_movel))

        time.sleep(1)

    else:
        print('espere')





