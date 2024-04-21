#импор библиотек для работы с Telegram API
import telebot 
from copy import deepcopy 
from bot_token import TOKEN 

bot = telebot.TeleBot(TOKEN)

users_info = {}



locations = {
    '1': {'text': 'Вы игратет за героя, который попал в опасный лес Чинджу где царит вечная ночь 🌙 . Вам нужно найти выход в город Инадзума и не попаться на глаза Сёгун чтобы выжить. 🍀', 'items': [], 'next_move': {'Пройти вперед' : '2'}, 'exchange': {} },
    '2': {'text':  'Открыв глаза вы были очарованы лунными цветами, которые были разбросаны по всему таинственнуму лесу. Лёгкий туман и тихое сверчание внушают спокойствие, но не слишком расслабляйтесь, ходят слухи, что, прогуливаясь по лесу Чинджу, вы можете столкнуться с таинственными существами, которые любят проказничать. 🤫', 'items': [], 'next_move':{'Пойти налево': '3',
                                                                    'Пойти прямо': '4',
                                                                    'Пойти направо': '5'}, 'exchange':{} },
    '3': {'text': 'Вы свернули с тропы и прошли чуть глубже в лес Чинджу, и заметили как пробежала темная фигура. Вы остановились чтобы остожно осмотреться, но не успев и глазом моргнуть вы почувствовали  как сзади на вас что-то бежит. Вы стали жертвой Сёгун ❗', 'items': [], 'next_move': {}, 'exchange': {}},
    '4': {'text': 'Вы вышли на заброшенную тропу. Перед вами тануки. Вреда они, конечно, не причинят, но обманут и запутают без труда. Однако, если поиграть с ними, можно получить награду.', 'items': [], 'next_move': {'Вернуться назад' : '2'},'exchange': {'шкатулка' : 'золото: 3'} },
    '5': {'text': 'Вы оказались около заброшенного святилища Инадзумы, скрытое в глубине леса Чинджу.', 'items': [], 'next_move': {'Вернуться назад' : '2',
                                                     'Войти внутрь' : '7',
                                                     'Осмотреться вокруг' : '6'},'exchange':{}},
    '6': {'text': 'Осматривая вокруг, вы замечаете старые врата тории ⛩️, красный цвет котрых давно побледнел, но несмотря на это они не утратили своего величия и давали окутаться в атмосферу инадзумского храма. Вы немного еще побродили в надежде что-то найти', 'items': ['шкатулка'], 'next_move': {'Вернуться к подземелью': '5'}, 'exchange':{}},
    '7': {'text': 'Здесь стены полностью закрыты грубым камнем на котором вы заметили странные символы. В воздухе царит прохлада и сырость. Легенда гласит, что в прошлом этот храм был домом для многих демонов.', 'items': ['золото: 2'], 'next_move':{'Пойти вперед' : '8',
                                                                                                        'Выйти на улицу' : '5'}, 'exchange':{}},
    '8': {'text': 'Вы проходите дальше. Здесь повсюду можно найти статуи Тануки. Вдруг в далеке вы замечаете свет', 'items': [], 'next_move': {'Пойти дальше' : '9', 
                                                                                              'Вернуться' : '7'}, 'exchange':{}},
    '9': {'text': 'Концовка не за горами, но прохождение не обойдется без дополнительных расходов 💰 ', 'items': [], 'next_move': {'Вернуться назад' : '8'}, 'exchange': {'золото: 5' : 'выход'}}                                                                                      

}

def generate_story(user, position):
    #берем текстовое описание локации 
    txt = locations[position]['text']
    #и создаем клавиатуру 
    keyboard = telebot.types.InlineKeyboardMarkup()
    for i in users_info[user]['loc'][position]['next_move']:
        #берем текст направления 
        key_txt = i
        #берем название локации 
        key_data = locations[position]['next_move'][i]
        keyboard.add (telebot.types.InlineKeyboardButton (text=key_txt, callback_data = key_data))
    
    #создаем кнопки для предметов которые можно взять 
    for i in users_info[user]['loc'][position]['items']:
        #берем название предмета 
        key_txt = 'Взять предмет - ' + i
        key_data = 'item' + i 
        keyboard.add (telebot.types.InlineKeyboardButton (text=key_txt, callback_data = key_data))
    
    #создем кнопки для предметов которыми можем обменяться 
    for i in users_info[user]['loc'][position]['exchange']:
        #проверим есть ли у нас нужный предмет для обмена и необходимое количество монет 
       if i in users_info[user]['items'] or (i.startswith('золото: ') and users_info[user]['coins'] >= int (i.replace ('золото: ', ''))):
            #генерируем текст обмена 
            key_txt = 'Обменять предмет ' + i + ' на ' + users_info[user]['loc'][position]['exchange'][i]
            #в callback_data добавим в начало 'exchange'
            key_data = 'exchange' + i
            keyboard.add (telebot.types.InlineKeyboardButton (text=key_txt, callback_data = key_data))
    
    return(txt, keyboard)




@bot.message_handler(commands=['game'])
def start_game(message):
    #добавляем пользователя в словарь с значением по умолчанию
    users_info[message.from_user.username] = {'cur_pos' : '1', 'coins' : 0, 'items' : [], 'loc': deepcopy ( locations )}
    txt, keyboard = generate_story (message.from_user.username, users_info[message.from_user.username]['cur_pos'])
    bot.send_message(message.chat.id, txt, reply_markup=keyboard)


#если call.data в ключах словаря locations 
@bot.callback_query_handler(func=lambda call: call.data in locations)
def callback_query(call):
    #меняем текущую позицию пользователя 
    users_info[call.from_user.username]['cur_pos'] = call.data
    #генерируем новый текст и кнопки 
    txt, keyboard = generate_story(call.from_user.username, users_info[call.from_user.username]['cur_pos'])
    #отправляем сообщение 
    bot.send_message(call.message.chat.id, txt, reply_markup=keyboard)



# если call.data начинается с item
@bot.callback_query_handler(func=lambda call: call.data.startswith('item '))  
def callback_query(call) :
    #берем название предмета ( в строке заменяем подстроку 'item' на  ' ')
    item= call.data.replace('item', '')
    #если предмет начинается на 'золото:' то добавляем пользователю монеты 
    if item.startswith('золото: '):
        users_info[call.from_user.username]['coins'] += int(item.replace('золото: ', ''))
    else: 
    #иначе просто добавляем в список предметов 
        users_info[call.from_user.username]['items'].append (item)
    #чтобы повторно не взять этот предмет  удаляем его с карты локаций  
    users_info[call.from_user.username]['loc'][users_info[call.from_user.username]['cur_pos']]['items'].remove(item)
    bot.send_message(call.message.chat.id, 'Готово')
    txt, keyboard =  generate_story(call.from_user.username, users_info[call.from_user.username]['cur_pos'])
    bot.send_message(call.message.chat.id, txt, reply_markup=keyboard)



  # если call.data начинается с 'exchange'
    
@bot.callback_query_handler(func=lambda call: call.data.startswith('exchange '))
def callback_query(call):
    #меняем 'exchange' на ''
    item1 = call.data.replace('exchange ', '')
    item2 = users_info[call.from_user.username]['loc'][users_info[call.from_user.username]['cur_pos']]['exchange'][item1]
   
    #если item1 начинается с 'золото':
    if item1.startswith('золото '):
        users_info[call.from_user.username]['coins'] -= int(item1.replace('золото: ', ''))
    else:
        users_info[call.from_user.username]['items'].remove(item1)



# если мы меняем на золото 
    if item2.startswith('золото '):
        #увеличиваем баланс
        users_info[call.from_user.username]['coins'] += int(item2.replace('золото: ', ''))
    else:
        #иначе добавляем нам предмет
        users_info[call.from_user.username]['items'].append(item2)
    users_info[call.from_user.username]['loc'][users_info[call.from_user.username]['cur_pos']]['exchange'].pop(item1)

    #если мы обменялись на выход, то выходит сообщение о победе 

    if item2 == 'выход':
        bot.send_message(call.message.chat.id, 'Тебе удалось пройти квест')

    else:
        bot.send_message(call.message.chat.id, 'Готово')
        txt, keyboard = generate_story(call.from_user.username, users_info[call.from_user.username]['cur_pos'])
        bot.send_message(call.message.chat.id, txt, reply_markup=keyboard)

if __name__ == '__main__':
    bot.infinity_polling()
