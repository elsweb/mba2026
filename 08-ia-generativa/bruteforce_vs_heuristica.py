import random
import string
import time


alfabeto = string.ascii_uppercase
tamanho = 6
inicio = time.perf_counter()
contador = 0
palavra = ""

for i in range(tamanho):
    contador += 1
    palavra = palavra + random.choice(alfabeto)

fim = time.perf_counter()

print("Palavra FORÇA BRUTA:", palavra)
print("Iterações:", contador)
print("Tempo:", fim - inicio, "segundos")


guardrail = [
    "abelha", "abacate", "amarelo", "amizade", "anel", "animal", "arvore", "areia", "banana", "barco",
    "barata", "bateria", "beleza", "bicicleta", "bola", "borboleta", "brasil", "cadeira", "caderno", "cafe",
    "cachorro", "caixa", "camisa", "caneta", "carro", "casa", "castelo", "celular", "cenoura", "chuva",
    "cidade", "computador", "cozinha", "crianca", "dado", "dinheiro", "dinossauro", "doce", "elefante", "energia",
    "escola", "espelho", "estrela", "familia", "fantasia", "fazenda", "felicidade", "festa", "fogo", "floresta",
    "folha", "formiga", "fruta", "garfo", "garrafa", "gato", "girafa", "goiaba", "hospital", "igreja",
    "ilha", "janela", "jardim", "jornal", "laranja", "leao", "leite", "livro", "lua", "madeira",
    "maquina", "mar", "melancia", "mesa", "montanha", "motor", "navio", "noite", "oculos", "orelha",
    "ovelha", "paisagem", "papel", "passaro", "pedra", "peixe", "pessoa", "piano", "ponte", "porta",
    "praia", "predio", "professor", "queijo", "relogio", "rio", "sapato", "sol", "telefone", "vento"
]

# Sílabas comuns do português
silabas = [
    "ba","be","bi","bo","bu",
    "ca","ce","ci","co","cu",
    "da","de","di","do","du",
    "fa","fe","fi","fo","fu",
    "ga","ge","gi","go","gu",
    "la","le","li","lo","lu",
    "ma","me","mi","mo","mu",
    "na","ne","ni","no","nu",
    "pa","pe","pi","po","pu",
    "ra","re","ri","ro","ru",
    "sa","se","si","so","su",
    "ta","te","ti","to","tu",
    "va","ve","vi","vo","vu"
]

# Tamanho desejado
tamanho = 6

palavra = ""

# Contador de tentativas
iteracoes = 0

inicio = time.perf_counter()

while True:

    palavra = ""

    # Monta uma palavra usando sílabas
    while len(palavra) < tamanho:
        palavra = palavra + random.choice(silabas)

    # Corta caso passe do tamanho
    palavra = palavra[:tamanho]

    iteracoes += 1

    # Verifica se a palavra existe no dicionário
    if palavra in guardrail:
        break

fim = time.perf_counter()

print("Palavra HEURÍSTICA:", palavra)
print("Tentativas até encontrar:", iteracoes)
print("Tempo:", fim - inicio, "segundos")