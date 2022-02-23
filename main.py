import os
import sys
import requests
import logging
import arrow

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler

logging.basicConfig(
    level=logging.ERROR,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()

updater = Updater(os.getenv('TELEGRAM_TOKEN'))
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

URL = 'https://api.thedogapi.com/v1/images/search'


def get_new_image():
    try:
        response = requests.get(URL)
    except Exception as error:
        # print(error)
        logging.error(f'Ошибка пр запросе к API с котиками: {error}')
        new_url = 'https://api.thecatapi.com/v1/images/search'
        response = requests.get(new_url)

    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def new_dog(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_image())


def wake_up(update, context):
    write_me_who_is_user(update, context)

    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup([['/new_dog']], resize_keyboard=True)

    context.bot.send_message(
        chat_id=chat.id,
        text=f'Человек-друг, {name}!'
             f' Я нашел для тебя песика, зацени)',
        reply_markup=button,
    )

    context.bot.send_photo(chat.id, get_new_image())


def write_me_who_is_user(update, context):
    chat = update['message']['chat']
    z = arrow.get(update['message']['date'])
    date = z.to('UTC+3')
    username = chat['username']
    first_name = chat['first_name']
    last_name = chat['last_name']
    id = chat['id']
    special_message = (
        f'Твоим ботом воспользовался @{username} \n'
        f'Это было в эту дату и время {date} \n'
        f'Вот информация о нём: \n'
        f'Имя: {first_name} \n'
        f'Фамилия: {last_name} \n'
        f'id в телеграмм: id{id} \n'
    )
    context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=special_message)


def main():
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CommandHandler('new_dog', new_dog))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
