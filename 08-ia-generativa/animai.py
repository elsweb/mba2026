import csv
import random
import nltk
import pandas as pd
from difflib import SequenceMatcher

from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

# =========================
# LOAD CSV
# =========================

knowledge = []

url = "https://raw.githubusercontent.com/elsweb/mba2026/refs/heads/main/08-ia-generativa/anime_chat_dataset.csv"

df = pd.read_csv(url)

knowledge = df.to_dict(orient="records")

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

    best_match = None
    best_score = 0

    for item in knowledge:

        trigger = item['user_input'].lower()

        score = similarity(text, trigger)

        if score > best_score:
            best_score = score
            best_match = item

    if best_score > 0.5:
        return best_match['response']

    return random.choice([
        "Interessante 😄",
        "Me conte mais",
        "Entendi 😄",
        "Legal 😄"
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

        print("\nAnimai: Até mais 😄")
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