import telebot
import datetime
import json
import requests
from telebot import custom_filters
from telebot import StateMemoryStorage
from telebot.handler_backends import StatesGroup, State


state_storage = StateMemoryStorage()

bot = telebot.TeleBot("6474608268:AAH1y-R4mWRsTOSj2Y2ZNOMGNoEmVP3gmPY", state_storage=state_storage, parse_mode='Markdown')


class PollState(StatesGroup):
    name = State()
    age = State()


class HelpState(StatesGroup):
    wait_text = State()


text_poll = "Регистрация 👋"
text_button_1 = "Расскажи о себе ☺️"
text_button_2 = "Полезные ресурсы 💻"
text_button_3 = "Погода ☔️"
API = '05a79b3408ba4e7b355bafb84df4912a'


menu_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
menu_keyboard.add(
    telebot.types.KeyboardButton(
        text_poll,
    )
)
menu_keyboard.add(
    telebot.types.KeyboardButton(
        text_button_1,
    )
)

menu_keyboard.add(
    telebot.types.KeyboardButton(
        text_button_2,
    ),
    telebot.types.KeyboardButton(
        text_button_3,
    )
)


@bot.message_handler(state="*", commands=['start'])
def start_ex(message):
    bot.send_message(
        message.chat.id,
        'Привет! Что будем делать?',
        reply_markup=menu_keyboard)


@bot.message_handler(func=lambda message: text_poll == message.text)
def first(message):
    bot.send_message(message.chat.id, 'Супер! Как вас зовут?')
    bot.set_state(message.from_user.id, PollState.name, message.chat.id)


@bot.message_handler(state=PollState.name)
def name(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text
    bot.send_message(message.chat.id, 'Супер! Напишите свой возраст!')
    bot.set_state(message.from_user.id, PollState.age, message.chat.id)


@bot.message_handler(state=PollState.age)
def age(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['age'] = message.text
    bot.send_message(message.chat.id, 'Спасибо за регистрацию!', reply_markup=menu_keyboard)
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: text_button_1 == message.text)
def help_command(message):
    bot.send_message(message.chat.id, "Я являюсь тестовым ботом для выполнения домашнего задания марафона по Python!", reply_markup=menu_keyboard)


@bot.message_handler(func=lambda message: text_button_2 == message.text)
def help_command(message):
    bot.send_message(message.chat.id, "Да конечно, вот парочка полезных ресурсов:\n1 - [Сгенерирует фото по тексту 🏞️️](https://rudalle.ru/kandinsky22) \n"
                                      "2 - [Избавляет аудиозапись от шумов 🎧](https://audo.ai/)\n"
                                      "3 - [Раскрашивает черно-белые снимки 🖼️](https://palette.fm/)\n"
                                      "4 - [Убирает ненужные объекты с фото 🔍](https://cleanup.pictures/)\n"
                                      "5 - [Увеличивает расмер фото и улучшает их качество 👁️‍🗨️](https://www.upscale.media/ru)", disable_web_page_preview=True, reply_markup=menu_keyboard)


def get_weather(message):
    city = 'Москва'
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&lang=ru&&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = int(data["main"]["temp"])
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        code_to_smile = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }
        weather_description = data["weather"][0]["main"]

        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотри в окно, я не понимаю, что там за погода..."
        bot.reply_to(message, f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
                              f'Температура: {temp} °C {wd}\n'
                              f'Влажность: {humidity} % \n'
                              f'Скорость ветра: {wind} м/с \n'
                              f'Удачи!')
    else:
        bot.reply_to(message, 'Город указан неверно')


@bot.message_handler(func=lambda message: text_button_3 == message.text)
def help_command(message):
    get_weather(message)
    bot.send_message(message.chat.id, "Это данные о погоде в Москве", reply_markup=menu_keyboard)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.TextMatchFilter())

bot.infinity_polling()
