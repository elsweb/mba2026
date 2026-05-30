import csv
import random
import nltk

from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

# =========================
# LOAD CSV
# =========================

knowledge = []

with open('anime_chat_dataset.csv', 'r', encoding='utf-8') as file:

    reader = csv.DictReader(file)

    for row in reader:

        knowledge.append(row)

# =========================
# NLTK
# =========================

sia = SentimentIntensityAnalyzer()

# =========================
# RESPONSE ENGINE
# =========================

def get_response(user_input):

    text = user_input.lower()

    matches = []

    for item in knowledge:

        trigger = item['user_input'].lower()

        if trigger in text:

            matches.append(item)

    if matches:

        selected = random.choice(matches)

        return selected['response']

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