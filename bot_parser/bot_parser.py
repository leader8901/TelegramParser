from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import csv

import environ

env = environ.Env()
environ.Env.read_env()


# Основной класс
class TeleParser:
    # Основной конструктор
    def __init__(self, api_id, api_hash, phone):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = TelegramClient(phone, api_id, api_hash)
        self.offset_id = 0
        self.limit = 200
        self.all_messages = []
        self.total_messages = 0
        self.total_count_limit = 0

    # Функция подключение и авторизации
    def connect(self):
        '''Подключение к клиентам телеграм'''
        self.client.start()
        print("Подключение ......")
        if not self.client.is_user_authorized():
            self.client.send_code_request(self.phone)
            try:
                self.client.sign_in(self.phone, input('Введите код подтверждения: '))
            except SessionPasswordNeededError:
                self.client.sign_in(password=input("Введите пароль: "))
        print('Клиент подключен.', end='\r')

    def get_chats(self):
        """Получение всех чатов пользователя"""
        groups = [dialog for dialog in self.client.get_dialogs() if dialog.is_channel]
        print('Из какого чата вы хотите парсить участников:')
        [print(str(groups.index(g) + 1) + ' - ' + g.title) for g in groups]
        print('Выход - любой другой символ')
        self.choice_checker(groups)

    # Проверяем чтобы введенное было числом!
    def choice_checker(self, groups):
        if not (user_input := input("\nПожалуйста! Введите число: ")).isdigit() or \
                int(user_input) not in range(1, len(groups)):
            print('\nBye!\n')
            pass
        else:
            self.chat_scraper(groups[int(user_input) - 1])

    def chat_scraper(self, target_group):
        """Сбор участников чата"""
        print('Сбор участников...', end='\r')
        users = [user.username for user in self.client.get_participants(target_group) if
                 user.username]
        print(f'Scraped {len(users)} members!')
        while (answer := input('\nВы хотите сохранить c сообщениями(1):  без сообщений(2): или отмена (3)?  ')) not in [
            '1', '2', '3']:
            print('Выбериет 1,2,3')
        if answer == '1':
            print('Сохранение в файл...')
            with open('users', 'w+') as f:
                [f.write(user + '\n') for user in users]
                f.close()
            print('Готово!')
            self.get_message(target_group)
        elif answer == '2':
            print('Сохранение в файл...')
            with open('users', 'w+') as f:
                [f.write(user + '\n') for user in users]
                f.close()
            print('Готово!')
        elif answer == '3':
            return self.get_chats()

    def get_message(self, target_group):
        print('Парсим сообщения.....')
        while True:
            history = self.client(
                GetHistoryRequest(peer=target_group, offset_id=self.offset_id, offset_date=None, add_offset=0,
                                  limit=self.limit,
                                  max_id=0,
                                  min_id=0,
                                  hash=0))
            if not history.messages:
                print('Не нашлось')
                break
            messages = history.messages
            for message in messages:
                self.all_messages.append(message.message)
            self.offset_id = messages[len(messages) - 1].id
            if self.total_count_limit != 0 and self.total_messages >= self.total_count_limit:
                print(self.all_messages)

    def save_message(self):
        print("Сохраняем данные в файл...")
        with open("chats.csv", "w+", encoding="UTF-8") as f:
            writer = csv.writer(f, delimiter=",", lineterminator="\n")
            for message in self.all_messages:
                writer.writerow([message])
        print('Парсинг сообщений группы успешно выполнен.')


if __name__ == '__main__':
    api_id = env('api_id')
    api_hash = env('api_hash')
    phone = env('phone')
    # Создаем объект и присваиваем
    new_obj = TeleParser(api_id, api_hash, phone)
    new_obj.connect()
    new_obj.get_chats()
