import telebot
import requests

Token = '7094792264:AAEH-QrZhteAOaFoHoCZEk54iyzhud1Tck4'
bot = telebot.TeleBot(Token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Please send an image for classification.")

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{Token}/{file_info.file_path}"
    response = requests.post("http://127.0.0.1:5000/predict", files={"file": requests.get(file_url).content})
    data = response.json()
    bot.reply_to(message, f"Class: {data['class']}\nConfidence: {data['confidence']}\nAdditional Info: {data['additional_message']}")

bot.polling()