import MetaTrader5 as mt5

mt5.initialize()

ativo = "PETR4"

selecionado = mt5.symbol_select(ativo, True)

info_simbolo = mt5.symbol_info(ativo)

info_simbolo_dict = mt5.symbol_info(ativo)._asdict()

for prop in info_simbolo_dict:
    print("{} = {}".format(prop, info_simbolo_dict[prop]))

mt5.shutdown()