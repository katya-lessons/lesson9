import socket
import threading

from PyQt6.QtWidgets import QMainWindow, QApplication

import client_chat


# пишем своё MainWindow, основанное на Ui_MainWindow (которое мы ранее сгенерировали)
class Chat(QMainWindow, client_chat.Ui_MainWindow):
    def __init__(self):
        # в методе инициализации мы вызываем родительскую инициализацию (устанавливаем элементы интерфейса)
        super(Chat, self).__init__()
        self.setupUi(self)

        # создаем сокет и подключаемся к сокет-серверу
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('127.0.0.1', 5060))

        # прописываем сигналы и слоты
        # (прописываем события, при отлавливании которых должны выполняться указанные функции)
        # в данном случае сигналы - это события (clicked),
        # а слоты - это функции, которые нужно выполнить (nickname_was_chosen, write)
        self.ok.clicked.connect(self.nickname_was_chosen)
        self.send.clicked.connect(self.write)

    # функция, которая выполняется при нажатии кнопки "ОК"
    def nickname_was_chosen(self):
        # открываем возможность ввода сообщения
        self.msg_line.setEnabled(True)
        self.send.setEnabled(True)
        # блокируем возможность ввода другого никнейма
        self.nickname.setEnabled(False)
        self.ok.setEnabled(False)

        # отправляем сокет-серверу введённый никнейм
        self.client.send(self.nickname.text().encode('ascii'))

        # стартуем поток, который постоянно будет пытаться получить сообщения
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    # метод для получения сообщений от других клиентов
    def receive(self):
        while True:
            try:
                # пытаемся получить сообщение
                message = self.client.recv(1024).decode('ascii')
                # если полученное сообщение с информацией не о введеном нике или не о своем сообщении,
                # добавляем сообщение в список
                if not message.startswith("NICK") and not message.startswith(self.nickname.text()):
                    self.messages.append(message)
            except:
                # в случае любой ошибки лочим открытые инпуты и выводим ошибку
                self.msg_line.setText("Error! Reload app")
                self.msg_line.setEnabled(False)
                self.send.setEnabled(False)
                # закрываем клиент
                self.client.close()
                break

    # метод, который отправляет сообщение серверу
    def write(self):
        # составляем сообщение
        message = '{}: {}'.format(self.nickname.text(), self.msg_line.text())
        # добавляем его в общий список сообщений
        self.messages.append(message)
        # удаляем текст с поля ввода сообщения
        self.msg_line.setText('')
        # отправляем сообщение серверу
        self.client.send(message.encode('ascii'))


if __name__ == "__main__":
    # при запуске клиента мы создаем инстанс приложения, созданного нами главного окна, и все запускаем
    app = QApplication([])
    window = Chat()
    window.show()
    app.exec()
