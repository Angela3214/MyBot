"""This is the code of my bot"""
from datetime import timedelta, date
import os
import sqlite3
import telebot

FORM = '{{:<{10}}}'
conn1 = sqlite3.connect('telegram_bot.db')
curs1 = conn1.cursor()
curs1.execute('''create table if not exists birthdays(id_tel varchar2(200),
note varchar2(1000), d_birthday date)''')
curs1.close()

#bot = telebot.TeleBot(os.environ['my_token'])
bot = telebot.TeleBot('5019599335:AAFvC46wOT3vX2GK-53gqLyJwBm8yQowWZM')

mp = dict()


@bot.message_handler(commands=['start'])
def button_message(message):
    """implementing buttons"""
    username = message.from_user.first_name
    bot.send_message(message.chat.id, 'Добро пожаловать, ' + username + "!")
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton("Добавить День Рождения")
    item2 = telebot.types.KeyboardButton("Удалить День Рождения")
    item3 = telebot.types.KeyboardButton("Вывести созданные данные")
    item4 = telebot.types.KeyboardButton("Проверить Дни Рождения")
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
    markup.add(item4)
    bot.send_message(message.chat.id, 'Выберите нужную функцию', reply_markup=markup)


def answer(label, message, human_id):
    """Implementing every label"""
    bot.send_message(human_id, 'Секундочку')
    conn3 = sqlite3.connect('telegram_bot.db')
    curs3 = conn3.cursor()
    if label == 1:
        ind_end_name = message.text.index('#')
        name = message.text[:ind_end_name]
        data = message.text[ind_end_name + 1:]
        if curs3.execute(
                f'insert into birthdays values(\'{human_id}\', \'{name}\', \'{data}\')'):
            conn3.commit()
            bot.send_message(human_id, 'Ух ты, успешно добавил!')

    elif label == 2:
        text = message.text
        curs3.execute(
            f'delete from birthdays where id_tel = {human_id} and note = \'{text}\'')
        curs3.execute(
            f'select * from birthdays where id_tel = {human_id} and note = \'{text}\'')
        test = curs3.fetchall()
        print(test)
        if not test:
            conn3.commit()
            bot.send_message(human_id, 'Я удалиль, теперь этого клоуна нет в твоих данных')
        else:
            bot.send_message(human_id, 'Ну я же попросил...Ошибка: такого пользователя нет')
    elif label == 3:
        tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m")
        if curs3.execute(
                f'select id_tel, note from birthdays where d_birthday like \'{tomorrow}%\''):
            for line in curs3.fetchall():
                bot.send_message(line[0], 'Не забудь поздравить ' + line[1] + ' с Днём Рождеия')
        else:
            bot.send_message(human_id, 'Никого неть :c')
    mp.pop(human_id)


@bot.message_handler(content_types='text')
def message_reply(message):
    """implementing answers"""
    conn = sqlite3.connect('telegram_bot.db')
    curs = conn.cursor()
    human_id = message.chat.id
    if human_id in mp.keys():
        answer(mp[human_id], message, human_id)
    if message.text == "Добавить День Рождения":
        bot.send_message(human_id,
                         'Для удобства использования вводите '
                         'уникальные записки пользователей')
        bot.send_message(human_id, 'Введите записку и дату рождения в формате ИМЯ#ДД.ММ.ГГГГ')
        mp[human_id] = 1
    elif message.text == "Удалить День Рождения":
        bot.send_message(human_id, 'Пожалуйста, вводите корректную записку, '
                                   'которую добавляли ранее')
        bot.send_message(human_id, 'Введите записку, которую желаете удалить')
        mp[human_id] = 2
    elif message.text == "Проверить Дни Рождения":
        mp[human_id] = 3
    elif message.text == "Вывести созданные данные":
        if curs.execute(
                'select note, d_birthday from birthdays where id_telegram = {hunam_id}'):
            for lines in curs.fetchall():
                bot.send_message(human_id, ''.join(FORM.format(line) for line in lines))
    curs.close()


def start():
    """Start out bot"""
    bot.polling(none_stop=True, interval=1)


@bot.message_handler(content_types='text')
def check():
    """Check birthday"""
    conn2 = sqlite3.connect('telegram_bot.db')
    curs2 = conn2.cursor()
    tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")
    curs2.execute(
        f'select id_tel, note from birthdays where v_birth_day = {tomorrow}')
    for line in curs2.fetchall():
        bot.send_message(line[0], 'Не забудь поздравить ' + line[1] + ' с Днём Рождеия')
    bot.polling(none_stop=True, interval=8)


start()
