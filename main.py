import time

import telebot
import zeep

# Инициализация Telegram бота
bot = telebot.TeleBot('6188095161:AAHVX4WKwvLIck9flZsH3y1-N8mxnwPU9-s')

# Настройки подключения к API
connect = {
    'wsdl': 'http://api.rossko.ru/service/v2.1/GetSearch',
    'options': {
        'connection_timeout': 1,
        'trace': True
    }
}

@bot.message_handler(content_types=['text'])
def mess(message):
    # Запрос значения text у пользователя
    bot.send_message(message.chat.id, 'Введите номер запчасти, VIN номер или номер кузова:')
    bot.register_next_step_handler(message, process_search)

# Обработчик команды /search
@bot.message_handler(commands=['search'])
def handle_search(message):
    # Запрос значения text у пользователя
    bot.send_message(message.chat.id, 'Введите значение для параметра text:')
    bot.register_next_step_handler(message, process_search)

# Обработка значения text и выполнение запроса к API
def process_search(message):
    text = message.text

    try:
        # Параметры запроса
        params = {
            'KEY1': '71e805856d8ddc8ab47c74c6b9b3266e',
            'KEY2': 'a48b652cb41df59dd744be33eb5c0de2',
            'text': text,
            'delivery_id': '000000001',
            'address_id': '112233'
        }

        # Выполнение запроса к API
        client = zeep.Client(connect['wsdl'])
        result = client.service.GetSearch(**params)

        # Обработка ответа и отправка результата пользователю
        handle_response(message.chat.id, result)
    except Exception as e:
        # Обработка ошибок
        bot.send_message(message.chat.id, f'Произошла ошибка: {str(e)}')

# Обработка ответа от API
def handle_response(chat_id, response):
    # Обработка данных из ответа
    success = response['success']
    text = response['text']
    message = response['message']
    parts = response['PartsList']['Part']

    # Формирование и отправка сообщения с результатом пользователю
    #result_message = f"Success: {success}\n"
    #result_message = f"Text: {text}\n"
    #result_message += f"Message: {message}\n"

    for part in parts:
        guid = part['guid']
        brand = part['brand']
        partnumber = part['partnumber']
        name = part['name']
        stocks = part['stocks']['stock']
        crosses = part['crosses']

        #result_message += f"\nGuid: {guid} |"
        result_message = f"Брэнд: <b>{brand}</b> |"
        result_message += f"Номер: {partnumber} |"
        result_message += f"Наименование: {name}\n\n"

        for stock in stocks:
            stock_id = stock['id']
            price = stock['price']
            count = stock['count']
            delivery_start = stock['deliveryStart']
            delivery_end = stock['deliveryEnd']

            #result_message += f"\nStock ID: {stock_id} |"
            result_message += f"Цена: <b>{price}</b>  |"
            result_message += f"Кол-во: {count} |"
            #result_message += f"Delivery Start: {delivery_start}\n"
            result_message += f"Доставка: {delivery_end}\n"

        if crosses:
            crosses_parts = crosses['Part']

            # Сортировка кроссов по Cross Price (по возрастанию)
            sorted_crosses = sorted(crosses_parts, key=lambda x: float(x['stocks']['stock'][0]['price']))

            # Ограничение вывода кроссов до 3 позиций
            limited_crosses = sorted_crosses[:3]

            result_message += "\nАналоги:\n"
            for cross_part in limited_crosses:
                cross_guid = cross_part['guid']
                cross_brand = cross_part['brand']
                cross_partnumber = cross_part['partnumber']
                cross_name = cross_part['name']
                cross_stocks = cross_part['stocks']['stock']

                #result_message += f"\nCross Guid: {cross_guid}\n"
                result_message += f"\nБрэнд: <b>{cross_brand}</b> \n\n"
                #result_message += f"Номер: {cross_partnumber} |"
                #result_message += f"Наименование: {cross_name}\n\n"

                for cross_stock in cross_stocks:
                    cross_stock_id = cross_stock['id']
                    cross_price = cross_stock['price']
                    cross_count = cross_stock['count']
                    cross_delivery_start = cross_stock['deliveryStart']
                    cross_delivery_end = cross_stock['deliveryEnd']

                    #result_message += f"\nCross Stock ID: {cross_stock_id} |"
                    result_message += f"Цена: <b>{cross_price}</b>  |"
                    result_message += f"Кол-во: {cross_count} |"
                    #result_message += f"Cross Delivery Start: {cross_delivery_start} |"
                    result_message += f"Доставка {cross_delivery_end}\n"

    # Разделение сообщения на части для отправки
    max_message_length = 4096  # Максимальная длина сообщения в Telegram (ограничение API)
    message_parts = [result_message[i:i + max_message_length] for i in
                        range(0, len(result_message), max_message_length)]

    # Отправка сообщений пользователю
    for part in message_parts:
        bot.send_message(chat_id, part, parse_mode='html')

# Запуск бота
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)