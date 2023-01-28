import datetime
from flask import Flask, request
from multiprocessing import Value
import os
import socket
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

counter = Value("i", 0)
app = Flask(__name__)

@app.route('/')
def hello():
    name = 'world'
    hostname = socket.gethostname()

    html = f"""
    <h1>Hello, {name}!</h1> 
    <b>Hostname:</b> {hostname} <br>
    """
    return html

@app.route('/about')
def about():
    name = os.getenv("NAME", 'world')
    hostname = socket.gethostname()

    html = f"""
    <h1>Hello, {name}!</h1> 
    <b>Hostname:</b> {hostname} <br>
    <b>Counter:</b> {counter.value}<br>
    """
    return html


@app.route('/stat')
def stat():

    import datetime

    headers = str(request.headers['User-Agent'])

    html = """
        <b>Datetime</b>: {d} <br>
        <b>Client User-Agent</b>: {req_headers}"""

    # Подключение к базе данных
    mydb = psycopg2.connect(host="psqldb",
                                   user="postgres",
                                   password="p@ssw0rd1",
                                   database="connections")

    # Установка курсора
    cursor = mydb.cursor()

    # Вставка данных о клиенте
    cursor.execute(f"INSERT INTO connection_logs VALUES ('{datetime.datetime.now()}','{str(request.headers['User-Agent'])}', '/stat')")

    # Коммит изменений
    mydb.commit()

    # Закрытие подключений
    cursor.close()
    mydb.close()

    counter.value += 1

    return html.format(d=datetime.datetime.now(), req_headers=headers)


@app.route('/initdb')
def db_init():

    # Подключение к хосту
    mydb = psycopg2.connect(host="psqldb",
                                   user="postgres",
                                   password="p@ssw0rd1") #psql
    
    # Определение уровня изоляции
    mydb.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    # Установка курсора
    cursor = mydb.cursor()

    # Удаление бд, если она уже существует
    cursor.execute("DROP DATABASE IF EXISTS connections")

    # Создание базы данных 
    cursor.execute("CREATE DATABASE connections")

    cursor.close()

    # Подключение к бзе данных
    mydb = psycopg2.connect(host="psqldb",
                                   user="postgres",
                                   password="p@ssw0rd1",
                                   database="connections")

    # Установка курсора
    cursor = mydb.cursor()

    # Удаление таблицы, если она существует
    cursor.execute("DROP TABLE IF EXISTS connection_logs")

    #создание таблицы
    cursor.execute("CREATE TABLE connection_logs (datetime timestamp DEFAULT NOW(), client VARCHAR(255), route VARCHAR(255))")

    # Вставка данных о клиенте
    cursor.execute(f"INSERT INTO connection_logs VALUES ('{datetime.datetime.now()}','{str(request.headers['User-Agent'])}', '/initdb')")

    # Коммит изменений
    mydb.commit()

    # Закрытие подлючения
    cursor.close()
    mydb.close()

    return 'init database'


@app.route('/clients')
def get_clients():


    mydb = psycopg2.connect(host="psqldb",
                                   user="postgres",
                                   password="p@ssw0rd1",
                                   database="connections")
    cursor = mydb.cursor()

    # Вставка данных о клиенте
    cursor.execute(f"INSERT INTO connection_logs VALUES ('{datetime.datetime.now()}','{str(request.headers['User-Agent'])}', '/clients')")

    # Коммит изменений
    mydb.commit()

    # Выполнение запроса
    cursor.execute("SELECT * FROM connection_logs")

    # Получение всех результатов
    results = cursor.fetchall()

    # Закрытие подлючения
    cursor.close()
    mydb.close()

    # Запись шапки таблицы
    res_str = """<table style="border: 3px double black;">
    <thead>
    <tr>
      <th><b>Time</b></th>
      <th><b>Client</b></th>
      <th><b>Route</b></th>
    </tr>
    <tbody>"""

    # Запись результатов запроса в таблицу
    for line in results:
        res_str += '<tr>'
        for element in line:
            res_str += f'<td>{element}</td>'
        res_str += '</tr>'

    # Закрытие тэгов таблицы
    res_str += """</tbody></table>"""

    return res_str


@app.route('/addlog')
def add_logs():

    # Подключение к базе данных
    mydb = psycopg2.connect(host="psqldb",
                                   user="postgres",
                                   password="p@ssw0rd1",
                                   database="connections")

    # Установка курсора
    cursor = mydb.cursor()

    # Вставка данных о клиенте
    cursor.execute(f"INSERT INTO connection_logs VALUES ('{datetime.datetime.now()}','{str(request.headers['User-Agent'])}', '/addlog')")

    # Коммит изменений
    mydb.commit()

    # Закрытие подключений
    cursor.close()
    mydb.close()

    return 'add_log'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)




# logs: время, клиент, маршрут
# вывод содержимого logs


# TODO: Добавить проверку существования БД/таблицы перед вставкой/чтением

# TODO: Вывод /clients таблицой;