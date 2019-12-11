print("Bot> Mohon ditunggu, saya sedang memuat semua dependencies yang dibutuhkan")
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job
import requests
import json
import re
import logging
import random
import nltk
from DocumentRetrievalModel import DocumentRetrievalModel as DRM
from ProcessedQuestion import ProcessedQuestion as PQ
import sys
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

#Start
def start(bot, update):
    update.message.reply_text("Assalamu'alaikum {}!"
		"\nSelamat datang di QasBot."
		"\nQasBot akan membantumu untuk menampilkan jawaban dari pertanyaan yang kamu ajukan berdasarkan terjemahan al quran surah Al-Baqarah."
		"\nKirim perintah /tanya <pertanyaan> untuk menampilkan jawaban dari pertanyaan yang diajukan"
		"\nKirim perintah /help untuk bantuan".format(update.message.from_user.first_name))


# Menampilkan pencarian kata pada Al-Qur'an
def tanya(bot, update, args):
	try:
		datasetName = "./dataset/albaqarah.txt"
		# Loading Dataset
		try:
			datasetFile = open(datasetName,"r")
		except FileNotFoundError:
			print("Bot> Oops! saya gagal menemukan direktori \"" + datasetName + "\"")
			exit()

		# Retrieving paragraphs : Assumption is that each paragraph in dataset is
		# separated by new line character
		paragraphs = []
		for para in datasetFile.readlines():
			if(len(para.strip()) > 0):
				paragraphs.append(para.strip())

		# Processing Paragraphs
		drm = DRM(paragraphs,True,True)

		print("Bot> Hey! Saya sudah siap.")
		print("Bot> Kamu dapat mengatakan Bye kapanpun kamu mau")

		# Greet Pattern
		greetPattern = re.compile("^\ *((hi+)|((good\ )?morning|evening|afternoon)|(he((llo)|y+)))\ *$",re.IGNORECASE)

		# isActive = True
		# while isActive:
		userQuery = " ".join(args)
		response = ''
		if(not len(userQuery)>0):
			print("Bot> Kamu perlu menanyakan sesuatu")

		elif greetPattern.findall(userQuery):
			response = "Hello!"
		elif userQuery.strip().lower() == "bye":
			response = "Bye Bye!"
			isActive = False
		else:
			# Proocess Question
			pq = PQ(userQuery,True,False,True)

			# Get Response From Bot
			response =drm.query(pq)

		
		qs = response
		if qs == '':
			update.message.reply_text("Tidak ada hasil pencarian untuk pertanyaan atau {}"
			"\nKirim perintah /tanya <pertanyaan> untuk menampilkan surat dan ayat apa saja dalam Al-Qur'an yang terdapat kata tersebut."
			"\nContoh :\n/tanya siapa penghuni neraka ?"
			.format(userQuery))
		else:
			# update.message.reply_text('Hasil pencarian untuk pertanyaan "{}"\n{}'.format(userQuery, qs))
			update.message.reply_text('"{}"'.format(qs))

	except (IndexError, ValueError):
		update.message.reply_text("Kirim perintah /tanya <pertanyaan> untuk menampilkan surat dan ayat apa saja dalam Al-Qur'an yang terdapat kata tersebut."
			"\nContoh :\n/tanya siapa penghuni neraka ?")


def help(bot, update):
    update.message.reply_text("/tanya <pertanyaan> : untuk menampilkan jawaban dari pertanyaan yang diajukan"
		"\n/help : bantuan".format(update.message.from_user.first_name))

def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Maaf, command yang kamu masukkan tidak ada. Kirim perintah /help untuk bantuan.")

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def main():
    updater = Updater('1022531797:AAExKb_DfXyI578PJ2tKzbUEO6OBTA_gHlA')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    # dp.add_handler(CommandHandler('quran', quran, pass_args=True))
    dp.add_handler(CommandHandler('tanya', tanya, pass_args=True))
    dp.add_handler(CommandHandler('help', help))
    
    dp.add_handler(MessageHandler([Filters.command], unknown))    
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()