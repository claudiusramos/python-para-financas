def CalculaMontante(capitalinicial, taxa, tempo):
    montante = capitalinicial * (1 + taxa) ** tempo

    return montante

capitalinicial = 2000
taxa = 2/100

for tempo in range(1,11):
    montante = CalculaMontante(capitalinicial, taxa, tempo)
    print("------Período {} -----".format(tempo))
    print("Montante = R$ {}".format(montante))
    print("-----------")
    print()
    print()
