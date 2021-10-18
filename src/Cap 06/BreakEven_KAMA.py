import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import time
import talib
import numpy as np

#configurar parametros de tela do pandas
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)


#iniciar metatrader
mt5.initialize()

#definir algumas variaveis importantes
ativo =  "WINM21"
selecionado = mt5.symbol_select(ativo)
stop_loss = 200
take_profit = 1000
qt_contratos = float(1)


def AtivaBreakEvent():
    return True

def VerificaHorarioOperacoes():
    # print('retorna o horario')
    horario_inicio_mercado = pd.Timestamp(datetime.today().strftime("%Y-%m-%d") + "-09:15:00")
    horario_meio_mercado = pd.Timestamp(datetime.today().strftime("%Y-%m-%d") + "-12:30:00")
    horario_tarde_mercado = pd.Timestamp(datetime.today().strftime("%Y-%m-%d") + "-15:00:00")
    horario_fechamento_mercado = pd.Timestamp(datetime.today().strftime("%Y-%m-%d") + "-16:30:00")

    hora_agora = datetime.now()
    print(hora_agora)

    if (hora_agora >= horario_inicio_mercado and hora_agora <= horario_meio_mercado) or (
            hora_agora >= horario_tarde_mercado and hora_agora <= horario_fechamento_mercado):
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

def venda(quantidade):
    print("ORDEM DE VENDA ENVIADA")
    lot = float(1)
    symbol = ativo
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).bid
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
        "magic": 10032021,
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
    price = mt5.symbol_info_tick(symbol).ask
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
        "magic": 10032021,
        "comment": "Ordem de Compra Enviada",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN
    }
    resultado = mt5.order_send(request)
    return resultado

#Aqui iniciamos o breakEven
breakEven = False

while True:
    if VerificaHorarioOperacoes() and ColetaValorDisponivel() > 200:
        total_ordens = mt5.positions_total()
        df = pd.DataFrame()
        df = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_M10, 1, 50)
        df = pd.DataFrame(df)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df.set_index('time')
        # Data Frame auxiliar
        dr = pd.DataFrame()
        dr = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_M10, 0, 1)
        dr = pd.DataFrame(dr)
        dr['time'] = pd.to_datetime(dr['time'], unit='s')
        dr = dr.set_index('time')
        df = df.append(dr)

        df['kama'] = talib.KAMA(df['close'].values, timeperiod=9)

        # Imprime o que tá acontecendo
        print('\n' + '=' * 50)
        print('NOVO SINAL | {}'.format(datetime.now()))
        print('=' * 50)
        print(df.iloc[-1].tail())

        preco_atual = df['close'].iloc[-1]
        valorIndicador = df['kama'].iloc[-1]
        diffMediaPrecoAtual = np.abs(valorIndicador - preco_atual)
        gatilho = 50

        breakEvenPontos = 50

        # Abertura de posicao
        print('DIFF:', diffMediaPrecoAtual)
        if (total_ordens == 0):
            breakEven = False
            if (preco_atual >= valorIndicador and diffMediaPrecoAtual <= gatilho):
                print(compra(qt_contratos))
            elif (preco_atual <= valorIndicador and diffMediaPrecoAtual <= gatilho):
                print(venda(qt_contratos))

        elif (total_ordens == 1):

            info_posicoes = mt5.positions_get(symbol=ativo)
            data_posicoes = pd.DataFrame(list(info_posicoes), columns=info_posicoes[0]._asdict().keys())

            # Diferenca do preco de operacao do preco atual
            diffAtualOperacao = np.abs(data_posicoes['price_open'][0] - preco_atual)
            precoOperacao = data_posicoes['price_open'][0]

            if(diffAtualOperacao >= 100):
                breakEven = AtivaBreakEvent()

            print("BREAKEVEN", breakEven)
            if(breakEven):
                if (data_posicoes['type'][0] == 0 and (preco_atual <= precoOperacao + breakEvenPontos or preco_atual <= valorIndicador)):
                    print(ordem_fechamento(str(data_posicoes['symbol'][0]),
                                           float(data_posicoes['volume'][0]),
                                           int(data_posicoes['ticket'][0]),
                                           data_posicoes['type'][0],
                                           int(data_posicoes['magic'][0]),
                                           0))

                    total_ordens = 0
                    breakEven = False
                    # print(venda(qt_contratos))
                if (data_posicoes['type'][0] == 1 and (preco_atual >= precoOperacao - breakEvenPontos or preco_atual >= valorIndicador)):
                    print(ordem_fechamento(str(data_posicoes['symbol'][0]),
                                           float(data_posicoes['volume'][0]),
                                           int(data_posicoes['ticket'][0]),
                                           data_posicoes['type'][0],
                                           int(data_posicoes['magic'][0]),
                                           0))

                    total_ordens = 0
                    breakEven = False
                    # print(compra(qt_contratos))

            if(not breakEven):
                if (data_posicoes['type'][0] == 0 and (
                        preco_atual <= valorIndicador and valorIndicador >= precoOperacao)):
                    print(ordem_fechamento(str(data_posicoes['symbol'][0]),
                                           float(data_posicoes['volume'][0]),
                                           int(data_posicoes['ticket'][0]),
                                           data_posicoes['type'][0],
                                           int(data_posicoes['magic'][0]),
                                           0))

                    total_ordens = 0

                if (data_posicoes['type'][0] == 1 and (
                        preco_atual >= valorIndicador and valorIndicador <= precoOperacao)):
                    print(ordem_fechamento(str(data_posicoes['symbol'][0]),
                                           float(data_posicoes['volume'][0]),
                                           int(data_posicoes['ticket'][0]),
                                           data_posicoes['type'][0],
                                           int(data_posicoes['magic'][0]),
                                           0))

                    total_ordens = 0    
    else:
        total_ordens = mt5.positions_total()
        print("FORA DO HORARIO DE NEGOCIACAO")
        print("TOTAL DE ORDENS: ", total_ordens)
        if (total_ordens == 1):
                info_posicoes = mt5.positions_get(symbol=ativo)
                data_posicoes = pd.DataFrame(list(info_posicoes), columns=info_posicoes[0]._asdict().keys())
            
                if (data_posicoes['type'][0] == 0):
                    print(ordem_fechamento(str(data_posicoes['symbol'][0]),
                                           float(data_posicoes['volume'][0]),
                                           int(data_posicoes['ticket'][0]),
                                           data_posicoes['type'][0],
                                           int(data_posicoes['magic'][0]),
                                           0))

                    total_ordens = 0

                if (data_posicoes['type'][0] == 1):
                    print(ordem_fechamento(str(data_posicoes['symbol'][0]),
                                           float(data_posicoes['volume'][0]),
                                           int(data_posicoes['ticket'][0]),
                                           data_posicoes['type'][0],
                                           int(data_posicoes['magic'][0]),
                                           0))

                    total_ordens = 0 

    time.sleep(1)

mt5.shutdown()