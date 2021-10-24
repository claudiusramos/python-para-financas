import matplotlib.pyplot as plt

def CalculaMontante(capitalinicial, taxa, tempo):
    montante = capitalinicial * (1 + taxa) ** tempo

    return montante

#Criar uma lista de anos
anos = list(range(31))

capitalinicial = 2000
taxa = 2/100

montantes = [CalculaMontante(capitalinicial,taxa,tempo) for tempo in anos]

plt.plot(anos, montantes)
plt.xlabel("Anos")
plt.ylabel("Capital")
plt.title("Juros Compostos")
plt.show()