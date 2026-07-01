import csv
import re
import random
import nltk
import pandas as pd
import sqlite3
from difflib import SequenceMatcher
from gensim.models import Word2Vec

from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

DB_NAME = "anime.db"

##########################################################
# CRIA O BANCO
##########################################################

def anime_database_init():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS anime (
            nome TEXT PRIMARY KEY,
            score REAL NOT NULL
        )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM anime")

    total = cursor.fetchone()[0]

    if total == 0:

        dados = [

            ("Solo Leveling", 4.9),
            ("One Piece", 4.9),
            ("Attack on Titan", 4.9),
            ("Naruto Shippuden", 4.8),
            ("Demon Slayer", 4.8),
            ("Jujutsu Kaisen", 4.8),
            ("Bleach Thousand-Year Blood War", 4.9),
            ("Chainsaw Man", 4.8),
            ("Black Clover", 4.8),
            ("My Hero Academia", 4.7),
            ("Spy x Family", 4.8),
            ("Dr. Stone", 4.8),
            ("Frieren", 4.9),
            ("The Apothecary Diaries", 4.9),
            ("Hunter x Hunter", 4.9),
            ("Death Note", 4.9),
            ("Haikyuu!!", 4.9),
            ("Blue Lock", 4.8),
            ("Fire Force", 4.7),
            ("Fullmetal Alchemist Brotherhood", 4.9)

        ]

        cursor.executemany(
            "INSERT INTO anime(nome,score) VALUES(?,?)",
            dados
        )

        conn.commit()

    conn.close()
    
##########################################################
# CONSULTA POR NOME
##########################################################

def anime_search(nome):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, score
        FROM anime
        WHERE nome LIKE ?
        ORDER BY score DESC
    """, (f"%{nome}%",))

    resultado = cursor.fetchall()

    conn.close()

    return resultado

##########################################################
# TOP ANIMES
##########################################################

def anime_top(limite=10):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, score
        FROM anime
        ORDER BY score DESC, nome
        LIMIT ?
    """, (limite,))

    resultado = cursor.fetchall()

    conn.close()

    return resultado

##########################################################
# INSERÇÃO
##########################################################

def anime_insert(nome, score):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO anime(nome,score)
        VALUES(?,?)
    """, (nome, score))

    conn.commit()
    conn.close()

anime_database_init()

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

print("=" * 60)
print("🤖 AniMai")
print("=" * 60)
print("Olá! Sou o AniMai.")
print("Posso conversar sobre animes e consultar minha base de dados.")
print()
print("Você pode dizer coisas como:")
print("- inserir anime")
print("- consultar score")
print("- melhores scores")
print("- sair")
print("=" * 60)

while True:

    user_input = input("\nVocê: ")

    texto = user_input.lower().strip()

    # =========================
    # SAIR
    # =========================

    if texto == "sair":

        print("\n🤖 AniMai: Obrigado pela conversa!")
        print("Até a próxima!")

        break

    # =========================
    # INSERÇÃO
    # =========================

    elif "inser" in texto or "cadastr" in texto or "adicionar" in texto:

        print("\n🤖 AniMai: Vamos cadastrar um anime.")

        nome = input("Nome do anime: ")

        while True:

            try:

                score = float(
                    input("Score: ").replace(",", ".")
                )

                break

            except ValueError:

                print("Digite um número válido.")

        anime_insert(nome, score)

        print(f"\n🤖 AniMai: '{nome}' foi cadastrado com score {score}.")  

    # =========================
    # TOP SCORES
    # =========================

    elif (
        "melhores" in texto
        or "top" in texto
        or "ranking" in texto
    ):

        resultado = anime_top()

        print("\n🏆 Ranking dos melhores animes\n")

        for posicao, (anime, score) in enumerate(resultado, start=1):
            print(f"{posicao:02d} - {anime} ({score})")
            
    
    # =========================
    # CONSULTA SCORE
    # =========================

    elif "score" in texto:

        nome = input("\nNome do anime: ")

        resultado = anime_search(nome)

        if resultado:

            print("\nResultado:")

            for anime, score in resultado:

                print(f"- {anime} | Score: {score}")

        else:

            print("\n🤖 AniMai: Não encontrei esse anime.")

    # =========================
    # CHAT INTELIGENTE
    # =========================

    else:

        sentiment = sia.polarity_scores(user_input)

        compound = sentiment["compound"]

        emotion = "neutro"

        if compound >= 0.5:

            emotion = "positivo"

        elif compound <= -0.5:

            emotion = "negativo"

        print(f"\n[Humor detectado: {emotion}]")

        response = get_response(user_input)

        print(f"\nAniMai: {response}")

print("=" * 60)
print("Sessão encerrada.")
print("=" * 60)