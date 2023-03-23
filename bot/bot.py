import os
from pathlib import Path
from PIL import Image

import telebot
from telebot import types

from gpt.gpt_chat import ChatGpt
from gpt.gpt_dalle import GptDalle
from common.common import parse_conf_file, get_file_size

token = parse_conf_file(key='TELEGRAM_TOKEN')
bot = telebot.TeleBot(token)
TIMEOUT = 60
# End of chating marker
is_chating = False
# Marker for creating image
is_image_markup = False
chatGpt = ChatGpt()
dalleGpt = GptDalle()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Hello!", reply_markup=home_markup())


@bot.message_handler(content_types=['photo'])
def handle_files(file):
    if is_image_markup:
        # TODO simplify code bottom
        download_dir = f'download/{file.from_user.username}'
        if not os.path.exists(download_dir):
            print(f"Creating directory: {download_dir} for downloded files")
            os.makedirs(download_dir)

        photo_file = file.photo[-1]  # biggest
        photo_file = bot.get_file(photo_file.file_id)
        downloaded_file = bot.download_file(photo_file.file_path)
        # Prepare to download file to server
        file_name = photo_file.file_unique_id + Path(photo_file.file_path).suffix
        temp_photo_file = Path(download_dir) / Path('tlg' + file_name)
        with open(Path(temp_photo_file), 'wb') as new_file:
            # Download file
            new_file.write(downloaded_file)
        # Converting to png
        img = Image.open(Path(temp_photo_file))
        png_file_path = Path(download_dir) / Path('tlg' + photo_file.file_unique_id + '.png')
        img.save(png_file_path, 'png')
        # Remove temp file
        os.remove(temp_photo_file)

        paths = dalleGpt.request_and_download(png_file_path, download_dir=download_dir)
        send_photo(paths, file.from_user.id)
    else:
        bot.send_message(file.from_user.id, "Please click on button in the bottom")


@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    global is_chating
    global is_image_markup
    chat_id = message.from_user.id

    if message.text == 'Home':
        # If we click on Home btn, reset markers to Off and finish chating
        is_chating = False
        is_image_markup = False
        # And clear gpt message history
        chatGpt.clear_history()

        bot.send_message(message.from_user.id, "Home markup", reply_markup=home_markup())
    elif message.text == "Chat with GPT":
        if not is_chating:
            # Start chating with GPT
            is_chating = True
            bot.send_message(chat_id, "Start chating with GPT. Please entering something:",
                             reply_markup=chat_gpt_markup())
        else:
            bot.send_message(chat_id, "You already chating with GPT. Typing something",
                             reply_markup=chat_gpt_markup())
    elif message.text == "Image creation":
        bot.send_message(chat_id,
                         "You can type some prompt that creates an image or send a picture to get a similar one",
                         reply_markup=dalle_gpt_markup())
        if not is_image_markup:
            is_image_markup = True

    else:
        # Continue chating with gpt
        if is_chating:
            answer = chatGpt.get_answer(message.text)
            bot.send_message(chat_id, answer)
        # Creating image by dalle
        if is_image_markup:
            paths = dalleGpt.request_and_download(message.text, download_dir=f'download/{message.from_user.username}')
            send_photo(paths, chat_id)


def send_photo(paths, chat_id):
    """
    Send photo or media grop
    :param paths: list with path to files
    :param chat_id:
    :return:
    """
    if len(paths) == 1:
        with open(Path(paths[0]), 'rb') as image:
            bot.send_photo(chat_id, image, timeout=TIMEOUT)
    else:
        album = []
        for path in paths:
            # TODO Add closing file
            album.append(types.InputMediaPhoto(open(Path(path), 'rb')))
        bot.send_media_group(chat_id, album, timeout=TIMEOUT)


def home_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Chat with GPT")
    btn2 = types.KeyboardButton("Image creation")
    markup.add(btn1, btn2)

    return markup


def chat_gpt_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Home")
    markup.add(btn1)

    return markup


def dalle_gpt_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Home")
    markup.add(btn1)

    return markup


# TODO change file_path on file IOStream
def is_size_allowed(file_path, max_image_size=4):
    """
    Check allowed image file size
    :param file_path: full file path
    :param max_image_size: allowed size for image in Mb
    :return:
    """
    try:
        with open(Path(file_path), 'rb') as image:
            file_size = get_file_size(file_path, 'mb')
            if file_size > max_image_size:
                return False
            return True
    except FileNotFoundError:
        print("File not found")


def pooling():
    bot.polling(none_stop=True, interval=0)
