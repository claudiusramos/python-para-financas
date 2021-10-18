#Coletando a Quantidade de Ativos Disponiveis
import MetaTrader5 as mt5

mt5.initialize()

simbolos = mt5.symbols_total()

if simbolos > 0:
    print("Total de simbolos encontrados: ", simbolos)
else:
    print("Nenhum simbolo encontrado")

mt5.shutdown()