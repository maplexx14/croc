# Импорт библиотек
import random
import time
import telebot
from telebot import types
from db import reg_db
from db import get_info
from db import init_db
from db import plus_ans
from db import delete_dup
from db import check_user

# Подключение к тг
bot = telebot.TeleBot('token')

# Файл с id пользователей
joinedFile = open('id.txt', 'r')
joinedUsers = set()
for line in joinedFile:
    joinedUsers.add(line.strip())
joinedFile.close()

# Файл с проголосовавшими пользователями
joinedFile1 = open('voted_users.txt', 'r')
joinedUsers1 = set()
for line in joinedFile1:
    joinedUsers1.add(line.strip())
joinedFile1.close()
# Рандомное число для рандомного слова
randNum = random.randint(1, 2600)
# Открытие файлов со словами
file = open('words.txt').readlines()
file1 = open('words_upper.txt').readlines()
arr_upper = [str(i) for i in file1]
arr = [str(i) for i in file]

# Переменные для фикса багов
count_play = 0
count_own = 0
own = None
word = None
guess_pem = None
total = 0
# Отображение статистики
@bot.message_handler(commands=['stat'])
def get_stat(message):
    count = 1
    try:
        for user in joinedUsers:
            user_info = (get_info(user_id=user))
            bot.send_message(message.chat.id,
                             f'[{user_info[2]}](tg://user?id={user}) - ' + f'{user_info[1]} ответов',
                             parse_mode='markdown')
            count += 1
    except Exception as e:
        print(e)
# Начало голосования для остановки игры
@bot.message_handler(commands=['stop'])
def stop_game(message):
    global total
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton('Проголосовать', callback_data='vote')
    markup.add(btn)
    bot.send_message(message.chat.id, 'Голосование за смену ведущего', reply_markup=markup)
    with open('voted_users.txt', 'w') as f:
        f.write('')
    return total
# Загадывание собственного слова
@bot.message_handler(commands=['own'])
def own_word(message):
    global guess_pem, count_own, word, current_player
    print(word, guess_pem, count_own)
    if guess is True or count_own != 0:
        bot.send_message(message.chat.id, 'Невозможно начать другую игру')
    else:
        current_player = message.from_user.id
        bot.send_message(chat_id,
                         f'[{message.from_user.first_name}](tg://user?id={message.from_user.id}) - вводит слово боту',
                         parse_mode='markdown')
        word = True
        own_wordd = bot.send_message(message.from_user.id, text='Введи слово, которое хочешь загадать')
        bot.register_next_step_handler(own_wordd, check_word)
        count_own += 1
        return word, count_own, current_player

# Начало работы 
@bot.message_handler(commands=['start'])
def start(message):
    global count_play, count_own,  count ,chat_id, word
    count_play = 0
    count_own = 0
    count = 0
    word = False
    chat_id = message.chat.id

    if not str(message.from_user.id) in joinedUsers:
        joinedFile = open('id.txt', "a")
        joinedFile.write(str(message.from_user.id) + '\n')
        joinedUsers.add(message.from_user.id)
        reg_db(user_id=message.from_user.id, answers=0, first_name=message.from_user.first_name)
    init_db()
    bot.send_message(message.chat.id,
                     '/play - начать обычную игру\n/own - загадать свое слово(слово нужно писать в лс боту)\n/stat - просмотреть статистику')

    print(message.chat.id)
    return count_play, count_own, count, chat_id, word

# Начало обычной игры
@bot.message_handler(commands=['play'])

def guess(message):
    global randNum, count_play, guess_pem, word, current_player
    print(word, count_play)
    if count_play == 0 and word is False:
        guess = True
        current_player = message.from_user.id
        btn = types.InlineKeyboardButton(text='Посмотреть слово', callback_data='slovo')
        btn1 = types.InlineKeyboardButton(text='Следующее слово', callback_data='sled', )
        markup = types.InlineKeyboardMarkup()
        markup.add(btn)
        markup.add(btn1)
        word = bot.send_message(message.chat.id,
                                f'[{message.from_user.first_name}](tg://user?id={message.from_user.id}) загадывает слово'
                                , parse_mode='markdown', reply_markup=markup)
        bot.register_next_step_handler(word, check)


        count_play += 1
        return randNum, guess, current_player

    else:
        bot.send_message(message.chat.id, 'Невозможно начать игру')
        
# Проверка слова на правильность
@bot.message_handler(content_types=['text'])
def check(message):
    global current_player, own, guess_pem, word, count_play, count, count_own, total
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton('Начать обычную игру', callback_data='host')
    btn1 = types.InlineKeyboardButton('Загадать свое слово', callback_data='own_new')
    markup.add(btn)
    markup.add(btn1)
    print(current_player)
    msg = message.text
    print(own)
    while msg != arr[randNum] or msg != arr[randNum + 1] or msg != own or msg != arr_upper[randNum] or msg != arr_upper[
        randNum + 1] and message.from_user.id != current_player:
        print(repr(msg + '\n'), repr(arr[randNum]), repr(arr_upper[randNum]))

        if (msg + '\n' == arr[randNum] or msg + '\n' == arr[randNum + 1] or msg + '\n' == arr_upper[
            randNum] or msg + '\n'
            == arr_upper[randNum + 1] or msg == own) and message.from_user.id != current_player:
            bot.send_message(message.chat.id,
                             text=f'[{message.from_user.first_name}](tg://user?id={message.from_user.id}) - отгадал слово *{message.text.lower()}*',
                             parse_mode='markdown', reply_markup=markup)
            isnot = str(check_user(user_id=message.from_user.id))
            print(isnot)
            guess_pem = False
            word = False
            count = 0
            own = ''
            arr[randNum] = ''
            arr_upper[randNum] = ''
            count_play = 0
            count_own = 0
            total = 0
            print(own)
            if isnot == '(0,)':
                reg_db(user_id=message.from_user.id, answers=1, first_name=message.from_user.first_name)
                break
            else:
                plus_ans(answers=1, user_id=message.from_user.id)
                current_player = message.from_user.id
                break
        else:
            return

    delete_dup()


def check_word(message):
    global own, chat_id
    own = message.text
    if own != '':
        bot.send_message(message.from_user.id, 'Слово принято')
        btn = types.InlineKeyboardButton(text='Просмотреть слово', callback_data='own')
        markup = types.InlineKeyboardMarkup()
        markup.add(btn)
        word = bot.send_message(chat_id,
                                f'[{message.from_user.first_name}](tg://user?id={message.from_user.id}) загадывает слово'
                                , parse_mode='markdown', reply_markup=markup)
        bot.register_next_step_handler(word, check)
    return own

# Ответы на нажатие Inline кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: types.CallbackQuery):
    global current_player, randNum, i, own, count_play, word, count, count_own
    if call.data == 'slovo' and call.from_user.id == current_player:
        arr[randNum] = arr[randNum + 1]
        bot.answer_callback_query(call.id, show_alert=True, text=f"Слово {arr[randNum]}")

    elif call.data == 'sled' and call.from_user.id == current_player:
        randNum = random.randint(1, 2621)
        bot.answer_callback_query(call.id, show_alert=True, text=f"Слово {arr[randNum + 1]}")
        bot.send_message(call.message.chat.id,
                         f'[{call.from_user.first_name}](tg://user?id={call.from_user.id}) решил заменить слово',
                         parse_mode='markdown')

        return randNum
    elif call.data == 'vote':
        global total, guess_pem
        if not str(call.from_user.id) in joinedUsers1:
            with open('voted_users.txt', 'w') as file:
                file.write(str(call.from_user.id) + '\n')

            bot.answer_callback_query(call.id, show_alert=True, text=f'Ваш голос засчитан')

            total += 1
        else:
            bot.answer_callback_query(call.id, show_alert=True, text=f'Вы уже проголосовали')
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('Проголосовать', callback_data='vote')
        markup.add(btn)


        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.id, text=f'Голосование за смену ведущего. Всего голосов {total}',reply_markup=markup)
        if total == bot.get_chat_member_count(call.message.chat.id) /2  or total > bot.get_chat_member_count(call.message.chat.id) / 2:
            bot.send_message(call.message.chat.id, f'Игра остановлена' , parse_mode='markdown')
            guess_pem = False
            word = False
            count = 0
            own = ''
            arr[randNum] = ''
            arr_upper[randNum] = ''
            count_play = 0
            count = 0
            count_own = 0
            total = 0
            print(current_player)

        print(bot.get_chat_member_count(call.message.chat.id))
    elif call.data == 'own_new':
        if count == 0:
            bot.answer_callback_query(call.id, show_alert=True, text='Введи свое слово самому боту')
            own_wordd = bot.send_message(call.from_user.id, text='Введи слово, которое хочешь загадать')
            bot.register_next_step_handler(own_wordd, check_word)
            count += 1
        else:
            bot.send_message(call.message.chat.id, 'Игра уже идет')

            return randNum, count
    elif call.data == 'own' and own != '' and call.from_user.id == current_player:
        bot.answer_callback_query(call.id, show_alert=True, text=f'Слово {own}')

    elif call.data == 'host':
        if count == 0:
            randNum = random.randint(1, 2621)
            current_player = call.from_user.id
            bot.answer_callback_query(call.id, show_alert=True, text=f'Теперь ты хост')

            btn = types.InlineKeyboardButton(text='Просмотреть слово', callback_data='slovo')
            btn1 = types.InlineKeyboardButton(text='Следующее слово', callback_data='sled')
            markup = types.InlineKeyboardMarkup()
            markup.add(btn)
            markup.add(btn1)
            bot.send_message(call.message.chat.id,
                             f'[{call.from_user.first_name}](tg://user?id={call.from_user.id}) загадывает слово'
                             , parse_mode='markdown', reply_markup=markup)
            bot.register_next_step_handler(call.message, check)
            count += 1
        else:
            bot.send_message(call.message.chat.id, 'Игра уже идет')

            return randNum, count

    else:
        bot.answer_callback_query(call.id, show_alert=True, text='Тебе недоступно это слово')


print('Бот запущен')


# Зацикливание бота
while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
        time.sleep(15)






