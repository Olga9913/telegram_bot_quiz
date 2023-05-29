import sqlite3
import sys

class SQLiteDB:

    def __init__(self):
        self.db = sqlite3.connect(sys.path[0] + '/database.db')
        self.db.execute('CREATE TABLE IF NOT EXISTS USERS(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, '
                        'Username TEXT UNIQUE, Count_questions INTEGER, Count_correct INTEGER);')
        self.db.execute('CREATE TABLE IF NOT EXISTS QUESTIONS(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, '
                        'Userid INTEGER, Status INTEGER, Image TEXT, A0 TEXT, A1 TEXT, A2 TEXT, A3 TEXT, '
                        'Rigth_answer INTEGER);')
        self.db.commit()
        self.db.row_factory = sqlite3.Row

    def add_user(self, username):
        self.db.execute(f"INSERT OR IGNORE INTO USERS(Username, Count_questions, Count_correct) "
                        f"VALUES ('{username}', 0, 0);")
        self.db.commit()

    def add_question(self, username, file, a0, a1, a2, a3, acor):
        self.add_user(username)
        self.db.execute(f"INSERT INTO QUESTIONS(Userid, Status, Image, A0, A1, A2, A3, Rigth_answer) "
                        f"VALUES ((SELECT Id FROM USERS WHERE Username = '{username}'), 0, '{file}', "
                        f"'{a0}', '{a1}', '{a2}', '{a3}', {acor});")
        self.db.commit()

    def last_question(self, username, ans):
        c = self.db.cursor()
        c.execute(f"SELECT A0, A1, A2, A3, Rigth_answer FROM QUESTIONS WHERE Userid = (SELECT Id FROM USERS WHERE "
                  f"Username = '{username}') AND Status = 0 ORDER BY Id DESC LIMIT 1;")
        r = c.fetchone()
        if r[4] == 0:
            rstr = r[0]
        elif r[4] == 1:
            rstr = r[1]
        elif r[4] == 2:
            rstr = r[2]
        elif r[4] == 3:
            rstr = r[3]
        if r[4] == ans:
            self.db.execute(f"UPDATE USERS SET Count_questions = Count_questions + 1, "
                            f"Count_correct = Count_correct + 1 WHERE Username = '{username}';")
            result = f"Верно, {rstr}"
        else:
            self.db.execute(f"UPDATE USERS SET Count_questions = Count_questions + 1 WHERE Username = '{username}';")
            result = f"Неверно, правильный ответ: {rstr}"
        self.db.execute(f"UPDATE QUESTIONS SET Status = 1 WHERE Userid = (SELECT Id FROM USERS WHERE "
                        f"Username = '{username}');")
        self.db.commit()
        return result

    def get_top(self, username, n):
        c = self.db.cursor()
        c.execute(f"SELECT Username, Count_questions, Count_correct FROM USERS ORDER BY Count_correct DESC LIMIT {n};")
        values = c.fetchall()
        result = []
        i = 0
        for item in values:
            i = i + 1
            tmp = {k: item[k] for k in item.keys()}
            tmp['Place'] = i
            result.append(tmp)
        if not any(d['Username'] == username for d in result):
            c.execute(f"SELECT Count_questions, Count_correct FROM USERS WHERE Username = '{username}';")
            r = c.fetchone()
            c.execute(f"SELECT COUNT(*) FROM USERS WHERE Count_correct > '{r[1]}';")
            p = c.fetchone()
            result.append({'Username': username, 'Count_questions' : r[0], 'Count_correct' : r[1], 'Place' : p[0] + 1})
        return result

    def __del__(self):
        self.db.commit()
        self.db.close()

