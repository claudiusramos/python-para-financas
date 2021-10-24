#Declarando as variáveis
capitalinicial = 1000
taxa = 3/100


for tempo in range(1,11):
    print("------Período {}------".format(tempo))
    print("Capital Inicial = R$ {}".format(capitalinicial))
    juros = capitalinicial * taxa
    print("Juros ganhos = R$ {}".format(juros))
    capitalinicial = capitalinicial + juros
    print("Montante = R$ {}".format(capitalinicial))
    print("--------------")
    print()
    print()