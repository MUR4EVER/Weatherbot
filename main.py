import requests
import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from translations import translations
from translations import messages
from aiogram.types import ReplyKeyboardRemove

bot = Bot(token="6492070147:AAFLSH7sPcx-j8xC0iJpEvPerUPnBbQRiVg")
dp = Dispatcher(bot)

LANGUAGES = {
    'en': 'English🇬🇧',
    'ru': 'Русский🇷🇺',
}

user_languages = {}

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):

    if message.from_user.id not in user_languages:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        language_row = [KeyboardButton('Language / Язык')]
        keyboard.add(*language_row)
        await message.reply('Hello! To get started, choose a language to use the bot.🌐\n\n '
                            'Привет! Для начала выбери язык, чтобы пользоваться ботом.🌐', reply_markup=keyboard)
    else:
        await message.reply('Hello! To get started, choose a language to use the bot.🌐\n\n '
                            'Привет! Для начала выбери язык, чтобы пользоваться ботом.🌐')

@dp.message_handler(lambda message: message.text == 'Language / Язык' or message.text == '/language')
async def language_settings_command(message: types.Message):
    language_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    language_row = [KeyboardButton(lang_name) for code, lang_name in LANGUAGES.items()]
    language_keyboard.add(*language_row)

    await message.reply("Выберите язык / Select a language: ", reply_markup=language_keyboard)

@dp.message_handler(lambda message: message.text in LANGUAGES.values())
async def select_language(message: types.Message):
    lang_code = 'en'
    for code, lang_name in LANGUAGES.items():
        if message.text == lang_name:
            user_languages[message.from_user.id] = code
            lang_code = code
            await message.reply(messages[lang_code]['language_set'].format(lang_name))

    await message.reply(messages[lang_code]['prompt_city'], reply_markup=ReplyKeyboardRemove())

@dp.message_handler()
async def get_weather(message: types.Message):
    lang_code = user_languages.get(message.from_user.id, 'en')

    code_to_smile = {
        "Clear": {"en": "Clear ☀️", "ru": "Ясно☀️"},
        "Few clouds": {"en": "Partly cloudy 🌤️", "ru": "Облачно🌤️"},
        "Scattered clouds": {"en": "Scattered clouds 🌥️", "ru": "Облачно🌥️"},
        "Broken clouds": {"en": "Broken clouds 🌦️", "ru": "Облачно🌦️"},
        "Clouds": {"en": "Cloudy ☁", "ru": "Облачно ☁"},
        "Rain": {"en": "Rain ☔", "ru": "Дождь ☔"},
        "Drizzle": {"en": "Drizzle ☔", "ru": "Ливень ☔"},
        "Thunderstorm": {"en": "Thunderstorm ⚡", "ru": "Гроза ⚡"},
        "Snow": {"en": "Snow 🌨", "ru": "Снег 🌨"},
        "Mist": {"en": "Mist 🌫", "ru": "Туман 🌫"},
        "Smoke": {"en": "Smoke 🌫", "ru": "Дымка 🌫"},
        "Clear sky": {"en": "Clear sky ☀️", "ru": "Чистое небо ☀️"},
    }

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={'a818d5f0a63025fc46ddf695d64e15ff'}&units=metric"
        )

        data = r.json()
        city = data["name"]
        weather_description = data["weather"][0]["main"]

        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description][lang_code]
        else:
            wd = translations[lang_code].get('wd_message', 'Look out the window, I dont understand the weather!')

        cur_weather = data["main"]["temp"]
        if cur_weather < -30:
            tm = translations[lang_code].get('extremely_cold')
        elif -10 >= cur_weather > -30:
            tm = translations[lang_code].get('very_cold')
        elif -10 <= cur_weather < 0:
            tm = translations[lang_code].get('cold')
        elif 0 <= cur_weather < 10:
            tm = translations[lang_code].get('cool')
        elif 10 <= cur_weather < 20:
            tm = translations[lang_code].get('warm')
        elif 20 <= cur_weather < 30:
            tm = translations[lang_code].get('hot')
        elif 30 <= cur_weather < 40:
            tm = translations[lang_code].get('very_hot')
        else:
            tm = translations[lang_code].get('extremely_hot')

        wind = data["wind"]["speed"]
        if wind < 5:
            wm = translations[lang_code].get('calm_wind')
        elif 5 <= wind < 10:
            wm = translations[lang_code].get('windy')
        elif 10 <= wind < 20:
            wm = translations[lang_code].get('strong_wind')
        else:
            wm = translations[lang_code].get('stormy')

        humidity = data["main"]["humidity"]
        if humidity < 10:
            hm = translations[lang_code].get('very_low_humidity')
        elif 10 <= humidity < 30:
            hm = translations[lang_code].get('low_humidity')
        elif 30 <= humidity < 80:
            hm = translations[lang_code].get('moderate_humidity')
        elif 80 <= humidity < 95:
            hm = translations[lang_code].get('humid')
        else:
            hm = translations[lang_code].get('very_high_humidity')

        await message.reply(
            f"{datetime.datetime.now().strftime('%d.%m.%Y')} "
            f"{translations[lang_code]['in_city']} <b>{city}</b>. "
            f"<b>{translations[lang_code]['temperature']}</b> {cur_weather}<b>°C</b> {wd},{tm} "
            f"<b>{translations[lang_code]['humidity']} {humidity}%</b>,{hm} <b>{translations[lang_code]['wind']} {wind} m/s</b>, {wm}",
            parse_mode="HTML"
        )

    except:
        await message.reply(messages[lang_code]['error'])


if __name__ == '__main__':
    executor.start_polling(dp)
