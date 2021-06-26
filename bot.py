# Import Libraries
import telebot
from config import token
import wikipedia
import pickle

# Telebot
bot = telebot.TeleBot(token)

# Open and load SVM models
vectorizer = pickle.load(open('vectorizer_model.pkl','rb'))
model = pickle.load(open('model.pkl','rb'))
vectorizer = pickle.load(open('vectorizer_model.pkl','rb'))
model = pickle.load(open('model.pkl','rb'))

# Wikiscrap and predict function 
def wikiData(response):
	try:
		page = wikipedia.page(response)
		data = page.summary
	except:
		topics = wikipedia.search(response)
		data = wikipedia.summary(topics[1])

	return model.predict(vectorizer.transform([data]))[0]

# Bot functions
@bot.message_handler(content_types=['text'])
def welcome(pm):
    sent_msg = bot.send_message(pm.chat.id, "Welcome to CBI. Send in the name of the first accused.")
    bot.register_next_step_handler(sent_msg, first_handler) #Next message will call the first_handler function
    
def first_handler(pm):
    first = pm.text
    sent_msg = bot.send_message(pm.chat.id, f"First accused is {first}. Send in the name of the second accused.")
    bot.register_next_step_handler(sent_msg, second_handler, first) #Next message will call the second_handler function

def second_handler(pm, first):
	second = pm.text
	if wikiData(first) == wikiData(second):
		bot.send_message(pm.chat.id, f"{first} and {second} are related. Both are from the field of {wikiData(first)}.")
	else:
		bot.send_message(pm.chat.id, f"They are not related.")
		
bot.polling()