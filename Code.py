import telebot
from telebot import types
import datetime
import sqlite3

format_string = '{{:<{}}}'.format(20)

# conn = sqlite3.connect('telegram_bot.db')
# curs = conn.cursor()
# curs.execute('''create table if not exists birthdays(id_telegram varchar2(200), v_birth_note varchar2(1000), d_birthday date)''')
# curs.close()

bot = telebot.TeleBot('2091843643:AAHUq-hDiXRnRJT8YIPN5b4DdKOvAB0azmA')
mp = dict()


@bot.message_handler(commands=['start'])
def button_message(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     'Теперь ты никогда не будешь забывать поздравить друзей с Днём Рождения, {}'.format(user_name))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Добавить День Рождения")
    item2 = types.KeyboardButton("Удалить День Рождения")
    item3 = types.KeyboardButton("Вывести созданные данные")
    markup.add(item1)
    markup.add(item2)
    markup.add(item3)
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
            bot.send_message(human_id, 'Пожалуйста, вводите уникальные записки пользователей')
            bot.send_message(human_id, 'Введите записку и дату рождения в формате ИМЯ#ДД.ММ.ГГГГ')
            ok = 1
            return
        elif message.text == "Удалить День Рождения":
            bot.send_message(human_id, 'Пожалуйста, вводите корректную записку, которую добавляли ранее')
            bot.send_message(human_id, 'Введите записку, которую желаете удалить')
            ok = 2
            return
        elif message.text == "Вывести созданные данные":
            if curs.execute('select v_birth_note, d_birthday from birthdays where id_telegram like \'{}\''.format(human_id)):
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
            if mp.get(message.text) == None:
                bot.send_message(human_id, 'Ну я же попросил...Ошибка: такого пользователя нет')
            else:
                mp.pop(message.text)
                bot.send_message(human_id, 'Я удалиль, теперь этого клоуна нет в твоих данных')
        ok = 0
        curs.close()

    except Exception as e:
        print(e)



def start():
    bot.polling(none_stop=True, interval=1)


'''@bot.message_handler(content_types='text')
def Check_birthday(message):
    for el in mp:
        impl_data = datetime.date(mp[el][4:], mp[el][2:4], mp[el][:2])
        if impl_data == datetime.date.today():
            bot.send_message(message.chat.id, 'Не забудь поздравить ' + el + ' с Днём Рождеия')
    bot.polling(none_stop=True, interval=8)'''
start()
