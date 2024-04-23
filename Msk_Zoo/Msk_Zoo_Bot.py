import telebot
from distr import TOKEN, red, TextException
from telebot import types
import time
import json

bot = telebot.TeleBot(TOKEN)

QUESTIONS = {
    "Какие способности вы бы мечтали развить у себя?": ['Летать', 'Дыхание под водой'],
    'Какие качества вы цените больше всего у других людей?': ['решительность', 'красота']

    }


@bot.message_handler(commands=['start'])
def start_(message):
    markup = types.InlineKeyboardMarkup()
    empty_button = types.InlineKeyboardButton(text="Начать Викторину", callback_data="/start_victorina")
    markup.add(empty_button)
    logo = open('MZoo-logo-hor-mono-white-rus-preview-RGB.jpg', 'rb')
    bot.send_photo(message.chat.id, logo,
                   caption='Привет дорогой друг! Предлагаю тебе пройти викторину и'
                           ' узнать какое у тебя тотемное животное!\n'
                           'Ответ можно выбрать только из представленных ниже'
                   , reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == '/start_victorina':
        start_victorina(call.message)


@bot.message_handler(commands=['victorina'])
def start_victorina(message):
    red.delete(message.chat.id)  # Удаляем ответы пользователя
    questions = QUESTIONS.copy()  # Создаем копию исходного словаря
    ask_question(message, questions)


def ask_question(message, questions):
    question, answers = questions.popitem()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    list_answers = [answers]
    for answer in answers:
        markup.add(answer)
    bot.send_message(message.chat.id, question, reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: handle_answer(msg, question, questions, list_answers))


def handle_answer(message, question, questions, list_answers):
    if message.text in str(list_answers):
        red.rpush(message.chat.id, message.text)
        if questions:
            ask_question(message, questions)
        else:
            show_results(message)
    else:
        time.sleep(1)
        bot.send_message(message.chat.id, 'Введены неверные данные, начните сначала')
        time.sleep(1)
        start_victorina(message)


def show_results(message):
    answers = red.lrange(message.chat.id, 0, -1)
    decoded_answers = [answer.decode('utf-8') for answer in answers]
    if decoded_answers == ['красота', 'Летать']:
        animal_image = 'kukushka.jpeg'
        animal_text = "Ваше тотемное животное КУКУШКА"
        bot.send_photo(message.chat.id, open(animal_image, 'rb'), animal_text)
        bot.register_next_step_handler(message, lambda msg: info_block(msg, animal_image, animal_text, decoded_answers))
        info_block(message, animal_image, animal_text, decoded_answers)

    elif decoded_answers == ['красота', 'Дыхание под водой']:
        animal_image = 'kaiman.jpeg'
        animal_text = "Ваше тотемное животное ЧЕРНЫЙ КАЙМАН"
        bot.send_photo(message.chat.id, open(animal_image, 'rb'), animal_text)
        bot.register_next_step_handler(message, lambda msg: info_block(msg, animal_image, animal_text, decoded_answers))
        info_block(message, animal_image, animal_text, decoded_answers)

    elif decoded_answers == ['решительность', 'Дыхание под водой']:
        animal_image = 'krokodil.jpeg'
        animal_text = "Ваше тотемное животное ТУПОРЫЛЫЙ КРОКОДИЛ!"
        bot.send_photo(message.chat.id, open(animal_image, 'rb'), animal_text)
        bot.register_next_step_handler(message, lambda msg: info_block(msg, animal_image, animal_text, decoded_answers))
        info_block(message, animal_image, animal_text, decoded_answers)

    elif decoded_answers == ['решительность', 'Летать']:
        animal_image = 'popugai.jpeg'
        animal_text = "Ваше тотемное животное ПОПУГАЙ!"
        bot.send_photo(message.chat.id, open(animal_image, 'rb'), animal_text)
        bot.register_next_step_handler(message, lambda msg: info_block(msg, animal_image, animal_text, decoded_answers))
        info_block(message, animal_image, animal_text, decoded_answers)


def info_block(message, animal_image, animal_text, decoded_answers):
    user_info = (message.from_user.first_name, animal_text, decoded_answers)
    bot.send_message(message.chat.id, f'Московский зоопарк — один из старейших зоопарков Европы с уникальной'
                                      f'коллекцией животных. Важная задача зоопарка — вносить вклад в '
                                      f'сохранение биоразнообразия планеты. При нынешних темпах развития '
                                      f'цивилизации к 2050 году могут погибнуть около 10 000 биологических'
                                      f' видов. «Возьми животное под опеку» — это одна из программ,'
                                      f' помогающих зоопарку заботиться о его обитателях. Программа'
                                      f'позволяет с помощью пожертвования на любую сумму внести свой '
                                      f'вклад в развитие зоопарка и сохранение биоразнообразия планеты.')

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Сайт Zooпарка", url="https://new.moscowzoo.ru")
    button2 = types.InlineKeyboardButton(text="Связаться с сотрудником",
                                         url=f"https://t.me/Vidence_Verity?text={user_info}")
    # button3 = types.InlineKeyboardButton(text="Обратная связь", callback_data="/feedback")
    button4 = types.InlineKeyboardButton(text="Поделиться в TG",
                                         url=f'https://t.me/share/url?url=https://t.me/Currency_Court_Bot&'
                                             f'text={animal_text}')
    button5 = types.InlineKeyboardButton(text="Поделиться в VK",
                                         url=f'https://vk.com/share.php?url=https://t.me/Currency_Court_Bot&'
                                             f'photo={animal_image}&title={animal_text}')
    button6 = types.InlineKeyboardButton(text="Начать сначала", callback_data="/start_victorina")
    markup.add(button1, button2, button4, button5, button6)
    bot.send_message(message.chat.id, "Нажав кнопку ниже можете перейти на сайт зоопарка. "
                                      "Отправить итоги прохождения куратору программы. "
                                      "Или может хотите пройти тест снова?", reply_markup=markup)

    bot.register_next_step_handler(message, start_victorina)


bot.polling()
