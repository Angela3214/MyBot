from datetime import timedelta, date
import os
import sqlite3
import telebot

format_string = '{{:<{10}}}'

conn1 = sqlite3.connect('telegram_bot.db')
curs1 = conn1.cursor()
curs1.execute(
    '''create table if not exists birthdays(id_telegram varchar2(200), 
    v_birth_note varchar2(1000), d_birthday date)''')
curs1.close()

bot = telebot.TeleBot(os.environ['my_tlabelen'])


@bot.message_handler(commands=['start'])
def button_message(message):
    """implementing buttons"""
    bot.send_message(message.chat.id,
                     'Теперь ты никогда не будешь забывать поздравить'
                     ' друзей с Днём Рождения, {message.from_user.first_name}')
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


def answer(label, conn, curs, message, human_id):
    if label == 1:
        ind_end_name = message.text.index('#')
        name = message.text[:ind_end_name]
        data = message.text[ind_end_name + 1:]
        if curs.execute(
                f'insert into birthdays values(\'{human_id}\', \'{name}\', \'{data}\')'):
            conn.commit()
            bot.send_message(human_id, 'Ух ты, успешно добавил!')

    elif label == 2:
        curs.execute(
            f'delete from birthdays where id_telegram = {human_id} and v_birth_note = \'{message.text}\'')
        curs.execute(
            f'select * from birthdays where id_telegram = {human_id} and v_birth_note = \'{message.text}\'')
        test = curs.fetchall()
        print(test)
        if not test:
            conn.commit()
            bot.send_message(human_id, 'Я удалиль, теперь этого клоуна нет в твоих данных')
        else:
            bot.send_message(human_id, 'Ну я же попросил...Ошибка: такого пользователя нет')
    elif label == 3:
        tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m")
        if curs.execute(
                f'select id_telegram, v_birth_note from birthdays where d_birthday like \'{tomorrow}%\''):
            for line in curs.fetchall():
                bot.send_message(line[0], 'Не забудь поздравить ' + line[1] + ' с Днём Рождеия')
        else:
            bot.send_message(human_id, 'Никого неть :c')


@bot.message_handler(content_types='text')
def message_reply(message):
    """implementing answers"""
    try:
        label = 0
        conn = sqlite3.connect('telegram_bot.db')
        curs = conn.cursor()
        human_id = message.chat.id
        if message.text == "Добавить День Рождения":
            bot.send_message(human_id,
                             'Для удобства использования вводите '
                             'уникальные записки пользователей')
            bot.send_message(human_id, 'Введите записку и дату рождения в формате ИМЯ#ДД.ММ.ГГГГ')
            label = 1
        elif message.text == "Удалить День Рождения":
            bot.send_message(human_id, 'Пожалуйста, вводите корректную записку, '
                                       'которую добавляли ранее')
            bot.send_message(human_id, 'Введите записку, которую желаете удалить')
            label = 2
        elif message.text == "Проверить Дни Рождения":
            label = 3
        elif message.text == "Вывести созданные данные":
            if curs.execute(
                    f'select v_birth_note, d_birthday from birthdays where id_telegram = {human_id}'):
                for lines in curs.fetchall():
                    bot.send_message(human_id, ''.join(format_string.format(line) for line in lines))
        answer(label, conn, curs, message, human_id)
        curs.close()

    except Exception as element:
        print(element)


def start():
    """Start out bot"""
    bot.polling(none_stop=True, interval=0)


@bot.message_handler(content_types='text')
def check():
    """Check birthday"""
    conn2 = sqlite3.connect('telegram_bot.db')
    curs2 = conn2.cursor()
    tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")
    curs2.execute(
        f'select id_telegram, v_birth_note from birthdays where v_birth_day = {tomorrow}')
    for line in curs2.fetchall():
        bot.send_message(line[0], 'Не забудь поздравить ' + line[1] + ' с Днём Рождеия')
    bot.polling(none_stop=True, interval=8)


start()
