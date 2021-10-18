#Coletando Informações sobre a Conta
import MetaTrader5 as mt5
import pandas as pd

mt5.initialize()

informacoes_conta = mt5.account_info()

informacoes_conta_dicionario = informacoes_conta._asdict()

# for prop in informacoes_conta_dicionario:
#     print("{} = {}".format(prop, informacoes_conta_dicionario[prop]))


data_frame = pd.DataFrame(list(informacoes_conta_dicionario.items()), columns=['property','value'])
print("informacoes da conta como dataframe")
print(data_frame)

mt5.shutdown()