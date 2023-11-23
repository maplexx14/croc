import sqlite3


def ensure_connections(func):
    """ Декоратор для подключения к СУБД: открывает соединение,
            выполняет переданную функцию и закрывает за собой соединение.
            Потокобезопасно!
        """

    def inner(*args, **kwargs):
        with sqlite3.connect('database.db') as conn:
            res = func(*args, conn=conn, **kwargs)
        return res

    return inner


@ensure_connections
def init_db(conn, force: bool = False):
    """ Проверить существование таблицы а иначе пересоздать её
           :param conn: подключение к СУБД
           :param force: явно пересоздать все таблицы
       """
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS users')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id      INTEGER NOT NULL,
            answers      INTEGER,
            first_name   STRING
        )
    ''')
    # Сохранить изменения
    conn.commit()


@ensure_connections
def reg_db(conn, user_id: int, answers: int, first_name: str):  # Добавление пользователя в таблицу users
    c = conn.cursor()
    c.execute('INSERT INTO users (user_id, answers, first_name) VALUES (?,+?, ?)',
              (user_id, answers, first_name))
    conn.commit()


@ensure_connections
def edit_db(conn, user_id: int, answers: int, first_name: str):  # Пересоздание пользователя по user_id в таблицу users
    c = conn.cursor()
    c.execute('UPDATE users SET answers=? WHERE user_id = ?, first_name= ?', (user_id, answers, first_name))
    conn.commit()


@ensure_connections
def check_user(conn, user_id: int):  # Проверка существования пользователя с данным user_id
    c = conn.cursor()
    c.execute('SELECT EXISTS(SELECT * FROM users WHERE user_id = ?)', (user_id,))
    return c.fetchone()


@ensure_connections  # Удаление пользователя из таблицы users
def delete_user(conn, user_id: int):
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE user_id=?', (user_id,))
    conn.commit()


@ensure_connections
def get_info(conn, user_id: int):  # Получение всей информации о пользователе из таблицы users
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    return c.fetchone()
@ensure_connections
def plus_ans(conn, user_id: int, answers: int):  # Получение всей информации о пользователе из таблицы users
    c = conn.cursor()
    c.execute("UPDATE users SET answers = answers + ? WHERE user_id = ?", (answers, user_id))
    return c.fetchone()
@ensure_connections
def delete_dup(conn):
    cursor = conn.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    unique_list = []

    for row in rows:
        if row[1:] not in [i[1:] for i in unique_list]:
            unique_list.append(row)
        else:
            conn.execute(f"""
                DELETE FROM users
                WHERE user_id={row[0]}
            """)
    conn.commit()
