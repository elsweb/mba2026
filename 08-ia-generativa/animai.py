import csv
import re
import random
import nltk
import pandas as pd
from difflib import SequenceMatcher
from gensim.models import Word2Vec

from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

# =========================
# LOAD CSV
# =========================

knowledge = []

url = "https://raw.githubusercontent.com/elsweb/mba2026/refs/heads/main/08-ia-generativa/anime_chat_dataset.csv"

df = pd.read_csv(url)

knowledge = df.to_dict(orient="records")

# =========================
# WORD2VEC
# =========================

texto_dataset = "\n".join(df["user_input"].astype(str).tolist())

texto_limpo = re.sub(r"[^\w\s]", "", texto_dataset.lower())

corpus = []

for linha in texto_limpo.split("\n"):

    linha = linha.strip()

    if linha != "":
        corpus.append(linha.split())

modelo = Word2Vec(
    sentences=corpus,
    vector_size=100,
    window=5,
    min_count=1,
    workers=4,
    epochs=200
)

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# =========================
# NLTK
# =========================

sia = SentimentIntensityAnalyzer()

# =========================
# RESPONSE ENGINE
# =========================

def get_response(user_input):

    text = user_input.lower()

    # =========================
    # Primeira tentativa
    # =========================

    best_match = None
    best_score = 0

    for item in knowledge:

        trigger = item["user_input"].lower()
        score = similarity(text, trigger)

        if score > best_score:
            best_score = score
            best_match = item

    if best_score >= 0.7:
        return best_match["response"]

    # =========================
    # Segunda tentativa: Word2Vec
    # =========================

    best_match = None
    best_score = 0

    palavras = text.split()

    for i, palavra in enumerate(palavras):

        if palavra not in modelo.wv:
            continue

        similares = modelo.wv.most_similar(palavra, topn=10)

        for similar, _ in similares:

            nova_frase = palavras.copy()
            nova_frase[i] = similar
            frase = " ".join(nova_frase)

            for item in knowledge:

                trigger = item["user_input"].lower()

                score = similarity(frase, trigger)

                print(
                    f"{palavra} -> {similar} | "
                    f"score={score:.3f} | "
                    f"{frase}"
                )

                if score > best_score:
                    best_score = score
                    best_match = item

    print(f"Melhor score Word2Vec: {best_score:.3f}")

    if best_score >= 0.6:
        return best_match["response"]

    # =========================
    # Nenhuma correspondência
    # =========================

    return random.choice([
        "Interessante",
        "Me conte mais.",
        "Entendi",
        "Legal"
    ])

# =========================
# CHAT
# =========================

print("=" * 50)
print("CHAT CSV + NLTK")
print("=" * 50)

while True:

    user_input = input("\nVocê: ")

    if user_input.lower() == "sair":

        print("\nAnimai: Até mais")
        break

    # =========================
    # SENTIMENT
    # =========================

    sentiment = sia.polarity_scores(user_input)

    compound = sentiment['compound']

    emotion = "neutro"

    if compound >= 0.5:
        emotion = "positivo"

    elif compound <= -0.5:
        emotion = "negativo"

    print(f"\n[Humor detectado: {emotion}]")

    # =========================
    # RESPONSE
    # =========================

    response = get_response(user_input)

    print(f"\nAnimai: {response}")