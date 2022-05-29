from cmath import exp
from distutils.log import info
from re import U
from traceback import print_tb
from typing import final
from unittest import expectedFailure
import MySQLdb
import datetime


def connect_db():
    db_conn = MySQLdb.connect(host="i54jns50s3z6gbjt.chr7pe7iynqr.eu-west-1.rds.amazonaws.com",
                        user="es02x51u4l8icggn",
                        passwd="gwoh7xpr6cx27rlc",
                        db="mrktgasg5781u8t6", 
                        port=3306)
    return db_conn

def save_code(auth_code, cpr):
    db = connect_db()
    try:
        cursor = db.cursor()
        cursor.execute('UPDATE users SET auth_code = "{}" WHERE cpr = "{}"'.format(auth_code, str(cpr)))
        print("Code saved")
        db.commit()
    finally:
        db.close()

def get_info(cpr):
    db = connect_db()
    try:
        info = []
        cursor = db.cursor()
        cursor.execute('SELECT phone, email FROM users WHERE cpr = "{}"'.format(str(cpr)))
        for row in cursor.fetchone():
            info.append(row)
        return info
    finally:
        db.close()

def get_auth_code(cpr):
    db = connect_db()
    code = []
    try:
        cursor = db.cursor()
        cursor.execute('SELECT auth_code FROM users WHERE cpr = "{}"'.format(str(cpr)))
        for row in cursor.fetchone():
            code.append(row)
        return str(code[0])
    finally:
        db.close()

def save_mes_code(mes_code, cpr):
    db = connect_db()
    try:
        cursor = db.cursor()
        cursor.execute('UPDATE users SET mes_code = "{}" WHERE cpr = "{}"'.format(mes_code, str(cpr)))
        db.commit()

    finally:
        db.close()
    return mes_code

def validate_token(token):
    db = connect_db()
    try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE mes_code = {}'.format(token))
        for row in cursor.fetchone():
            print("")
        return True
    except:
        print("Token is not valid")
        return False
    finally:
        db.close()

#------------------------------ KAFKA ------------------------------

def get_messages(topic, last_message_id, limit):
    db = connect_db()
    try:
        cursor = db.cursor()
        output = []
        mes = []
        cursor.execute('SELECT * FROM {} WHERE id > {} ORDER BY id ASC LIMIT {}'.format(topic, last_message_id, limit))
        for row in cursor.fetchall():
            id, message, exp = row
            mes.append({"id": id, "message": message, "exp": exp})
        return mes
    finally:
        db.close()

def create_message(topic, message):
    db = connect_db()
    try:
        cursor = db.cursor()
        exp = datetime.datetime.now() + datetime.timedelta(days=7)
        print(exp)
        print(topic)
        cursor.execute('INSERT INTO {} (message, exp) VALUES ("{}","{}")'.format(topic, message, exp))
        db.commit()
        print("Message created")
        return True
    except:
        print("Message not created")
        return False
    finally:
        db.close()

def update_message(topic, message, id):
    new_time = datetime.datetime.now() + datetime.timedelta(days=7)
    db = connect_db()
    try:
        cursor = db.cursor()
        cursor.execute('UPDATE {} SET message = "{}", exp = "{}" WHERE id = {}'.format(topic, message, new_time, id))
        db.commit()
        print("Message updated")
        return True
    except:
        print("Message not updated")
        return False
    finally:
        db.close()

def delete_message(topic, id):
    db = connect_db()
    try:
        cursor = db.cursor()
        cursor.execute('DELETE FROM {} WHERE id = {}'.format(topic, id))
        db.commit()
        print("Message deleted")
        return True
    except:
        print("Message not deleted")
        return False
    finally:
        db.close()
    



