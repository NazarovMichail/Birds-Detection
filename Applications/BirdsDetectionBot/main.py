from config import TOKEN
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from keyboards import kbrd_menu, inline_dove, inline_bluetit, inline_thrush, inline_sparrow, inline_woodpecker, inline_cardinal
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# Подключение модели по API Roboflow
from roboflow import Roboflow
rf = Roboflow(api_key="jyxqZLcJ27mR9wFxBpUJ")
project = rf.workspace().project("birds-detection-fld02")
model = project.version(2).model


bot = Bot(TOKEN)  # Создание экземпляра бота с токеном
storage = MemoryStorage()  # Создание хранилища для буфера обмена
dispatcher = Dispatcher(bot, storage=storage)  # Создание обработчика сообщений


PROJECT_INFO = """
Бот разработан для детекции птиц по фото.
_____________________________________
📸 1. Загрузите фотографию с изображением птиц 

🦅 2. Бот определит птиц на фотографии 

📚 3. Чтобы узнать о птице подробнее 

   нажмите на кнопку "Узнать о ..." 
_____________________________________

В проекте принимали участие:
🤝 <b>Назаров М.С</b> : Разработка телеграмм-бота, 

🤝 <b>Новиков. В.В.</b> : Модель машинного обучения,

🤝 <b>Мельницын В.В.</b> : Тестирование телеграмм-бота

🤝 <b>Поливода А.Ю.</b> : Тестирование телеграмм-бота
...

"""


START_TEXT = """
<b>Загрузите фотографию птиц 🐦‍⬛️</b>
"""

# Функция при запуске бота
async def bot_startup(dispatcher):
    print('Bot is running ...')


# Функция при выходе из бота
async def bot_shutup(dispatcher):
    # При выходе пишется сообщение
    print('Bot has gone ...')


# Функция при получении сообщения "О проекте"
@dispatcher.message_handler(Text(equals='О проекте'))
async def proj_info(message: types.Message):
    await message.answer(text=f' {PROJECT_INFO} ',
                        parse_mode= "HTML")  # Выводится текст "PROJECT_INFO"
    await message.delete()  # Входящее сообщение удаляется


# Функция при получении команды "/start"
@dispatcher.message_handler(commands=['start'])
async def get_keyboard(message: types.Message):
    await message.answer(text=START_TEXT, parse_mode='HTML', reply_markup=kbrd_menu)  # Выводится текст "START_TEXT" и клавиатура главного меню
    await bot.send_animation(chat_id=message.from_user.id, animation=open('img/presentation.gif', 'rb'))  # Выводится gif-презентация
    await message.delete()


# Функция при получении входящей фотографии
@dispatcher.message_handler(content_types=['photo'])
async def get_photo(message: types.Message):   
    await message.photo[-1].download('model/file.jpg')  #  Фото сохраняется на сервер
    prediction = model.predict('model/file.jpg', confidence=40, overlap=30).json()  # Скачанное фото помещается в модель МО и возвращается json с детектированными птицами
    model.predict("model/file.jpg", confidence=40, overlap=30).save("model/prediction.jpg") # Фото с детектированными птицами сохраняется на сервер
    await message.delete()
    await bot.send_photo(chat_id=message.from_user.id, photo=open('model/prediction.jpg', 'rb'))  # Фото с детектированными птицами отправляется в бот
    
    class_list = []  # Список для всех детектированных птиц
    try:
        if prediction['predictions'] == []:
                await message.answer(text="""На изображении нет птиц 🤷... Ведь так? 🫣""")  # Если птицы не детектированы, выводится сообщение
        for pred in prediction['predictions']:  # Проходим по списку со всеми детектированными птицами
            if pred['class'] not in class_list:  # Если птица еще не возвращалась в боте
                if pred['class'] == "pigeon":  # Если детектированная птица - голубь
                    # В бот возвращается фото птицы из сервера и кнопка " Узнать о голубе"
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/pigeon.jpg', 'rb'), caption='Голубь', reply_markup=inline_dove)
                    class_list.append(pred['class'])  # Название детектированной птицы добавляется в список всех детектированных птиц
                if pred['class'] == "tit":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/titmouse.jpg', 'rb'), caption='Синица', reply_markup=inline_bluetit)
                    class_list.append(pred['class'])

                if pred['class'] == "thrush":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/thrush.jpg', 'rb'), caption='Дрозд', reply_markup=inline_thrush,)
                    class_list.append(pred['class'])

                if pred['class'] == "sparrow":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/sparrow.jpg', 'rb'), caption='Воробей', reply_markup=inline_sparrow)
                    class_list.append(pred['class'])
                    
                if pred['class'] == "woodpecker":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/woodpckr.jpg', 'rb'), caption='Дятел', reply_markup=inline_woodpecker)
                    class_list.append(pred['class'])

                if pred['class'] == "cardinal":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/cardinal.jpg', 'rb'), caption='Красный кардинал', reply_markup=inline_cardinal)
                    class_list.append(pred['class'])
    except IndexError:
        await message.answer(text="""На изображении нет птиц 🤷... Ведь так? 🫣""")


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dispatcher=dispatcher,
                        on_startup=bot_startup,
                        skip_updates=True,
                        on_shutdown=bot_shutup)  # Активация функция при запуске и выходе из бота