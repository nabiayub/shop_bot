from decouple import config

TOKEN = config('TOKEN')
PAYMENT = config('PAYMENT')

def number_to_emoji(text):
    emoji_digits = {
        '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
        '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'
    }
    for digit, emoji in emoji_digits.items():
        text = text.replace(digit, emoji)

    return text
