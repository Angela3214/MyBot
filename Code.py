import telebot
from datetime import timedelta, date
import sqlite3
import os

format_string = '{{:<{}}}'.format(10)

conn = sqlite3.connect('telegram_bot.db')
curs = conn.cursor()
curs.execute(
    '''create table if not exists birthdays(id_telegram varchar2(200), v_birth_note varchar2(1000), d_birthday date)''')
curs.close()

#bot = telebot.TeleBot(os.environ['my_token'])
bot = telebot.TeleBot('5019599335:AAFvC46wOT3vX2GK-53gqLyJwBm8yQowWZM')


@bot.message_handler(commands=['start'])
def button_message(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     'Теперь ты никогда не будешь забывать поздравить друзей с Днём Рождения, {}'.format(user_name))
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


ok = 0


@bot.message_handler(content_types='text')
def message_reply(message):
    try:
        global ok
        conn = sqlite3.connect('telegram_bot.db')
        curs = conn.cursor()
        human_id = message.chat.id

        if message.text == "Добавить День Рождения":
            bot.send_message(human_id, 'Для удобства использования вводите уникальные записки пользователей')
            bot.send_message(human_id, 'Введите записку и дату рождения в формате ИМЯ#ДД.ММ.ГГГГ')
            ok = 1
            return
        elif message.text == "Удалить День Рождения":
            bot.send_message(human_id, 'Пожалуйста, вводите корректную записку, которую добавляли ранее')
            bot.send_message(human_id, 'Введите записку, которую желаете удалить')
            ok = 2
            return
        elif message.text == "Проверить Дни Рождения":
            ok = 3
        elif message.text == "Вывести созданные данные":
            if curs.execute('select v_birth_note, d_birthday from birthdays where id_telegram = {}'.format(human_id)):
                for lines in curs.fetchall():
                    bot.send_message(human_id, ''.join(format_string.format(line) for line in lines))

        if ok == 1:
            ind_end_name = message.text.index('#')
            name = message.text[:ind_end_name]
            data = message.text[ind_end_name + 1:]
            if curs.execute('insert into birthdays values(\'{}\', \'{}\', \'{}\')'.format(human_id, name, data)):
                conn.commit()
                bot.send_message(human_id, 'Ух ты, успешно добавил!')

        elif ok == 2:
            curs.execute('delete from birthdays where id_telegram = {} and v_birth_note = \'{}\''.format(human_id,
                                                                                                        message.text))
            curs.execute('select * from birthdays where id_telegram = {} and v_birth_note = \'{}\''.format(human_id,
                                                                                                           message.text))
            test = curs.fetchall()
            print(test)
            if not test:
                conn.commit()
                bot.send_message(human_id, 'Я удалиль, теперь этого клоуна нет в твоих данных')
            else:
                bot.send_message(human_id, 'Ну я же попросил...Ошибка: такого пользователя нет')
        elif ok == 3:
            tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m")
            if curs.execute(
                'select id_telegram, v_birth_note from birthdays where d_birthday like \'{}%\''.format(tomorrow)):
                for line in curs.fetchall():
                    bot.send_message(line[0], 'Не забудь поздравить ' + line[1] + ' с Днём Рождеия')
            else:
                bot.send_message(human_id, 'Никого неть :c')

        ok = 0
        curs.close()

    except Exception as e:
        print(e)


def start():
    bot.polling(none_stop=True, interval=1)


@bot.message_handler(content_types='text')
def Check_birthday(message):
    conn = sqlite3.connect('telegram_bot.db')
    curs = conn.cursor()
    tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")
    curs.execute('select id_telegram, v_birth_note from birthdays where v_birth_day = {}'.format(tomorrow))
    for line in curs.fetchall():
        bot.send_message(line[0], 'Не забудь поздравить ' + line[1] + ' с Днём Рождеия')
    bot.polling(none_stop=True, interval=8)


start()
