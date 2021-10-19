import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def get_fund_inf(token,symbol):
    r = requests.get('https://lorraine.oplab.com.br/v3/market/stocks/%7B%7D?with_financials=dre,bpa,dfc,stocks,bpp,sector,fundamentals%27.format(symbol)', headers={"Access-Token": token})
    return r.json()

token_pedro = 'pgopHoNuMl7Vnc9pXxzSI9hF5juaGD54uOugO89KycDKFHRMm2zov1cA+XtFmfO/dFR8aRGC1CJs0bQ45Znocg==--hGaTd3F26BDUR1fExNmFsQ==--/LG8Gmuw/ce6m8w0LtD1Rg=='
meses_estudo = [3,6,9,12]
symbol = 'PETR4'
fig1, ax1 = plt.subplots(figsize = (20,10))
ordem_qs = []
maior_data = datetime(2012,1,1)
menor_data = maior_data

for i in meses_estudo:
    mes_estudo = i
    df = get_fund_inf(token_pedro, symbol)['financial']

    dre = pd.DataFrame(df)['dre'].dropna()
    bpa = pd.DataFrame(df)['bpa'].dropna()
    bpp = pd.DataFrame(df)['bpp'].dropna()
    dfc = pd.DataFrame(df)['dfc'].dropna()
#     sector = pd.DataFrame(df)['sector'].dropna()
#     fundamentals = pd.DataFrame(df)['fundamentals'].dropna()

    relatorio = bpa

    num_conta = '1'

    x = []
    y = []
    for d in list(relatorio.keys()):
        if isinstance(relatorio[d],dict):
            dt = datetime.strptime(d,'%Y-%m-%d')
            if dt.month == mes_estudo:
                x.append(dt)
                #print(relatorio[d][num_conta]['value'])
                y.append(relatorio[d][num_conta]['value'])
            nome_conta = relatorio[d][num_conta]['description']
    print(x)
    print(y)
    if len(x)==0:
        continue
    else:
        if np.min(x) < menor_data:
            menor_data = np.min(x)
        if np.max(x) > maior_data:
            maior_data = np.max(x)
        with plt.style.context('bmh'):
            if len(y) == 1:
                ax1.bar(x,y,width = 20)
            else:
                ax1.plot(x,y,linewidth = 6)
            #ax1.set_ylabel('{}'.format(nome_conta),fontsize=30)
        ordem_qs.append('Q{}'.format(int(mes_estudo/3)))

with plt.style.context('bmh'):
    closes = getFechamentosPorData(token,symbol,menor_data,datetime.today())
    ax1.legend(ordem_qs, fontsize=15, shadow=True, loc = 'best', ncol = 4)
    ax2 = ax1.twinx()
    ax2.plot(list(closes.index),list(closes['Adj Close']), color = 'black')
    ax2.set_ylabel('Preço'.format(symbol),fontsize=30)
    fig1.suptitle('{} X Preço {}'.format(nome_conta,symbol),fontsize=35)

    yy = entropia(list(closes['Adj Close']),21)
    yy_rank = iv_rank(entropia(list(closes['Adj Close']),21),120)
    fig2, ax1 = plt.subplots(1,1, figsize = (18,3))
    ax1.plot(list(closes.index),yy_rank,color = 'black')
    fig2.suptitle('Shannon_Rank {}'.format(symbol),fontsize=25)
    fig3, ax1 = plt.subplots(1,1, figsize = (18,3))
    ax1.plot(list(closes.index),yy,color = 'black')
    fig3.suptitle('Entropia de Shannon {}'.format(symbol),fontsize=25)

plt.show()