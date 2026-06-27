import re
from gensim.models import Word2Vec

letra_dataset = "Pane no sistema, alguém me desconfigurou Aonde estão meus olhos de robô? Eu não sabia, eu não tinha percebido Eu sempre achei que era vivo Parafuso e fluido em lugar de articulação Até achava que aqui batia um coração Nada é orgânico, é tudo programado E eu achando que tinha me libertado Mas lá vêm eles novamente Eu sei o que vão fazer Reinstalar o sistema Pense, fale, compre, beba Leia, vote, não se esqueça Use, seja, ouça, diga Tenha, more, gaste, viva Pense, fale, compre, beba Leia, vote, não se esqueça Use, seja, ouça, diga Não, senhor, sim, senhor Não, senhor, sim, senhor Pane no sistema, alguém me desconfigurou Aonde estão meus olhos de robô? Eu não sabia, eu não tinha percebido Eu sempre achei que era vivo Parafuso e fluido em lugar de articulação Até achava que aqui batia um coração Nada é orgânico, é tudo programado E eu achando que tinha me libertado Mas lá vêm eles novamente Eu sei o que vão fazer Reinstalar o sistema Pense, fale, compre, beba Leia, vote, não se esqueça Use, seja, ouça, diga Tenha, more, gaste, viva Pense, fale, compre, beba Leia, vote, não se esqueça Use, seja, ouça, diga Não, senhor, sim, senhor Não, senhor, sim, senhor Mas lá vêm eles novamente Eu sei o que vão fazer Reinstalar o sistema Adicionar aos favoritos Adicionar à playlist Tamanho do texto Cifra Imprimir Corrigir Rolagem automática"


# limpar texto
texto_limpo = re.sub(r"[^\w\s]", "", letra_dataset.lower())

# transformar em lista de frases
linhas = texto_limpo.split("\n")

corpus = []

for linha in linhas:
    if linha.strip() != "":
        palavras = linha.split()
        corpus.append(palavras)
        
        
modelo = Word2Vec(
    sentences=corpus,
    vector_size=50,
    window=3,
    min_count=1,
    workers=1
)

print("Palavras mais parecidas com 'robô':")
print(modelo.wv.most_similar("robô"))