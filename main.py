import random
import telebot
from telebot import types

# Создание игрового поля
board_size = 5
board = [["O" for _ in range(board_size)] for _ in range(board_size)]
bot_board = [["O" for _ in range(board_size)] for _ in range(board_size)]

# Функция для размещения кораблей на поле
def place_ships():
    ships = []
    num_ships = 3

    for _ in range(num_ships):
        ship = []
        ship_row = random.randint(0, board_size - 1)
        ship_col = random.randint(0, board_size - 1)
        ship.append(ship_row)
        ship.append(ship_col)
        ships.append(ship)
    return ships

# Размещение кораблей на поле игрока и бота
player_ships = place_ships()
bot_ships = place_ships()

# Функция для вывода игрового поля
def print_board(board):
    for row in board:
        print(" ".join(row))

# Создание телеграм-бота
bot = telebot.TeleBot("6118603347:AAHXdDzklE6cLB2WwOXUjL5CbE4m1e-8pNg")

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать в игру 'Морской бой'!")
    send_board(message.chat.id)
    send_bot_board(message.chat.id)

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "/restart":  # Обработка команды /restart
        restart_game(message.chat.id)
    else:
        # Получение координат выстрела от игрока
        if message.text.isdigit():
            guess_row = int(message.text)
            if guess_row >= 0 and guess_row < board_size:
                bot.send_message(message.chat.id, "Введите номер столбца (0-4):", reply_markup=create_keyboard())
                bot.register_next_step_handler(message, process_column_input, guess_row)
            else:
                bot.send_message(message.chat.id, "Неверный номер строки. Попробуйте еще раз.")
        else:
            bot.send_message(message.chat.id, "Неверный формат ввода. Пожалуйста, введите номер строки (0-4).")

# Создание клавиатуры для выбора столбца
def create_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("0", "1", "2", "3", "4")
    return keyboard

# Обработка ввода номера столбца
def process_column_input(message, guess_row):
    if message.text.isdigit():
        guess_col = int(message.text)
        if guess_col >= 0 and guess_col < board_size:
            player_hit = False
            for ship in bot_ships:
                if guess_row == ship[0] and guess_col == ship[1]:
                    player_hit = True
                    bot_ships.remove(ship)
                    break

            # Обновление поля игрока
            if player_hit:
                board[guess_row][guess_col] = "X"
                bot.send_message(message.chat.id, "Вы попали!")
            else:
                board[guess_row][guess_col] = "#"
                bot.send_message(message.chat.id, "Вы промахнулись!")

            # Проверка условия завершения игры
            if len(bot_ships) == 0:
                bot.send_message(message.chat.id, "Поздравляю! Вы победили!")
                return

            # Ход бота
            bot_guess_row = random.randint(0, board_size - 1)
            bot_guess_col = random.randint(0, board_size - 1)

            # Проверка попадания бота
            bot_hit = False
            for ship in player_ships:
                if bot_guess_row == ship[0] and bot_guess_col == ship[1]:
                    bot_hit = True
                    player_ships.remove(ship)
                    break

            # Обновление поля бота
            if bot_hit:
                bot_board[bot_guess_row][bot_guess_col] = "X"
                bot.send_message(message.chat.id, "Бот попал!")
            else:
                bot_board[bot_guess_row][bot_guess_col] = "#"
                bot.send_message(message.chat.id, "Бот промахнулся!")

            # Проверка условия завершения игры
            if len(player_ships) == 0:
                bot.send_message(message.chat.id, "К сожалению, вы проиграли.")
                return

            # Отправка игрового поля игрока
            send_board(message.chat.id)
            send_bot_board(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Неверный номер столбца. Попробуйте еще раз.")
    else:
        bot.send_message(message.chat.id, "Неверный формат ввода. Пожалуйста, введите номер столбца (0-4).")

# Функция для отправки игрового поля игрока
def send_board(chat_id):
    board_str = ""
    for row in board:
        board_str += " ".join(row) + "\n"
    bot.send_message(chat_id, "Игровое поле игрока:\n" + board_str)

# Функция для отправки игрового поля бота
def send_bot_board(chat_id):
    board_str = ""
    for row in bot_board:
        board_str += " ".join(row) + "\n"
    bot.send_message(chat_id, "Игровое поле бота:\n" + board_str)

# Функция для сброса состояния игры и перезапуска
def restart_game(chat_id):
    global board, bot_board, player_ships, bot_ships
    board = [["O" for _ in range(board_size)] for _ in range(board_size)]
    bot_board = [["O" for _ in range(board_size)] for _ in range(board_size)]
    player_ships = place_ships()
    bot_ships = place_ships()
    send_board(chat_id)
    send_bot_board(chat_id)

# Запуск телеграм-бота
bot.polling()
