import bs4
import requests
import os
import telebot
from flask import Flask, request
from config import token
from datetime import date
from html import escape

# Telebot
bot = telebot.TeleBot(token)


# Server deploy
server = Flask(__name__)
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
	bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
	return "!", 200

@server.route("/")
def webhook():
	bot.remove_webhook()
	bot.set_webhook(url='<HEROKU Web URL>' + TOKEN)
	return "!", 200



# Bot functions	
def getImg(photo_info, message):
	
	img_url = "https://api.telegram.org/file/bot%s/%s" % (token, photo_info.file_path)
	mess = bot.reply_to(message, "🔎 *Plase wait, CBI is onto this.*", parse_mode="Markdown")
	
	# Get search page
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14', 
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-language': 'en-US,en;q=0.9'}
	response = requests.get("https://www.google.com/searchbyimage?image_url=" + img_url, headers=headers)

	# Check for 429
	if response.status_code == 429:
		retry_after_text = "*429 Too Many Requests*\n\nGoogle limits the number of requests. It's not about you, but about the fact that a large number of people use the bot. Please try again later." \
		"\n\n_If you continue to spam, the situation will worsen not only for you but for others as well. Show respect._"
		bot.edit_message_text(message_id=mess.message_id, text=retry_after_text, parse_mode='Markdown', chat_id=message.chat.id)
		print("429 Too Many Requests")
		return

	# Parse all needed information
	b = bs4.BeautifulSoup(response.text, "html.parser")

	# Try parse suggestion
	try:
		find_sug = b.select('.fKDtNb')
		suggestion = find_sug[0].text
	except Exception as e:
		print(e, "No suggestion")
		suggestion = False

	# Try parse similar
	try:
		find_similar = b.select(".e2BEnf")
		similar = 'https://www.google.com' + str(find_similar[0].a['href'])
	except Exception as e:
		print(e, "No similar")
		similar = False

	# Try parse sites
	try:
		find_sites = b.find_all('div', {'class': 'rc'})
		sites = [(si.a['href'], si.h3.text) for si in find_sites]
	except Exception as e:
		print(e, "No sites")
		sites = False

	# Send
	txt = ''
	if suggestion:
		txt = '<b>This came up in the investigation: %s</b>\n\n' % escape(suggestion)

	txt += '<b>Case File:</b>\n\n'
	if sites:
		txt += '\n\n'.join([f'<a href="{escape(site[0])}">{escape(site[1])}</a>' for site in sites])

	markup = telebot.types.InlineKeyboardMarkup()
	if similar:
		markup.add(telebot.types.InlineKeyboardButton(text="🔗 Similar cases", url=similar))

	markup.add(telebot.types.InlineKeyboardButton(text="🌐 Search page", url=response.url))
	bot.edit_message_text(message_id=mess.message_id, text=txt, parse_mode='HTML', reply_markup=markup, chat_id=message.chat.id, disable_web_page_preview=True)


@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, "📥 You can send an image as *forwarded message* from any chat/channel or upload it as *Photo* or *File*.",
					parse_mode="Markdown")


@bot.message_handler(content_types=['photo'])
def photo(message):
	photo_info = bot.get_file(message.photo[0].file_id)
	getImg(photo_info, message)


@bot.message_handler(content_types=['document'])
def photo(message):
	photo_info = bot.get_file(message.document.file_id)
	getImg(photo_info, message)


if __name__ == "__main__":
	server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))