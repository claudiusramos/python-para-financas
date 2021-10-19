import MetaTrader5 as mt5
from datetime import datetime
import time
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import talib
import seaborn as sns
import statsmodels.api as sm

#configura parâmetros da biblioteca pandas
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1500)
pd.set_option('mode.chained_assignment', None)

#importando dados do ativo
ativo = 'PETR4'
mt5.initialize()
mt5.symbol_select(ativo)

df = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_D1, 0, 5000)
df = pd.DataFrame(df)
df['time'] = pd.to_datetime(df['time'], unit = 's')

#inicio aula machine learning
# print(df)

#Análise Exploratória
df['close'].plot(label = "PETR4", legend = True)
# plt.show()
# plt.clf()

#Rertonos
df['close'].pct_change().plot.hist(bins = 50)
# plt.xlabel("Retorno % Diário")
# plt.show()

pacote_de_dias = 3

#Criar nova variável 6 dias no futuro
df['dias_no_futuro'] = df['close'].shift(-pacote_de_dias)
df['dias_no_futuro_mudanca'] = df['dias_no_futuro'].pct_change(pacote_de_dias)
df['dias_atuais_mudanca'] = df['close'].pct_change(pacote_de_dias)

df = df.dropna()

correlacao = df[['dias_atuais_mudanca', 'dias_no_futuro_mudanca']].corr()

print("Correlacao: " + str(correlacao))
# plt.clf()
# plt.scatter(df['6d_atuais_mudanca'], df['6d_no_futuro_mudanca'])
# plt.show()



# obv
df['obv'] = talib.OBV(df['close'], df['real_volume'])
feature_names = ['dias_atuais_mudanca', 'obv']

for n in [2, 7, 9, 21, 50, 200]:
    #criar a media movel
    df['mme'+str(n)] = talib.EMA(df['close'].values, timeperiod = n)

    #criar indice de forca realativa (RSI)
    df['rsi' + str(n)] = talib.RSI(df['close'].values, timeperiod = n)

    feature_names = feature_names + ['mme' + str(n), 'rsi' + str(n)]

# print(feature_names)

df = df.dropna()

features = df[feature_names]
target = df['dias_no_futuro_mudanca']

feature_and_target = ['dias_no_futuro_mudanca'] + feature_names
feature_target_df = df[feature_and_target]
print(feature_target_df)

corr = feature_target_df.corr()
print("Correlacao: " + str(corr))

sns.heatmap(corr, annot = True, annot_kws= {"size": 5})
plt.yticks(rotation = 0, size = 8)
plt.xticks(rotation = 90, size = 8)
plt.tight_layout()
plt.show()
plt.clf()

plt.scatter(df['dias_no_futuro_mudanca'], df['rsi7'])
plt.show()

linear_features = sm.add_constant(features)

tamanho_treinamento = int(0.85 * features.shape[0])
variaveis_treinamento = linear_features[:tamanho_treinamento]
alvo_treinamento = target[:tamanho_treinamento]

variaveis_teste = linear_features[tamanho_treinamento:]
alvo_teste = target[tamanho_treinamento:]

print(linear_features.shape, variaveis_treinamento.shape, variaveis_teste.shape)


modelo = sm.OLS(alvo_treinamento, variaveis_treinamento)
resultado = modelo.fit()
print(resultado.summary())

print(resultado.pvalues)

previsoes_treinamento = resultado.predict(variaveis_treinamento)
previsoes_teste = resultado.predict(variaveis_teste)

plt.scatter(previsoes_treinamento, alvo_treinamento, alpha = 0.2, color = 'b', label = 'treinamento')
plt.scatter(previsoes_teste, alvo_teste, alpha= 0.2, color = 'r', label = 'teste')

xmin, xmax = plt.xlim()
plt.plot(np.arange(xmin, xmax, 0.01), np.arange(xmin, xmax, 0.01), c = 'k')

plt.xlabel('previsoes')
plt.ylabel('reais')
plt.legend()

plt.show()

