#!/usr/bin/env python3
"""Command-line based password manager utility."""

from hashlib import sha3_512
import sqlite3
from os import urandom

if __name__ == '__main__':
    USER_NAME = input("Enter your user name: ")
    CONN = sqlite3.connect('users.db')
    C = CONN.cursor()
    C.execute("CREATE TABLE IF NOT EXISTS users (user_name text, pass_hash text, salt text)")
    C.execute("SELECT * FROM users where user_name=?", (USER_NAME,))

    if not C.fetchone(): #If the username isn't in the database
        RESP = ''
        while RESP not in ('y', 'n'):
            RESP = input("User name not found." +
                         " Create a new user? (Y/N): ").lower()

        if RESP == 'y':
            USER_PASS = ''
            CONFIRM_PASS = ''
            while not USER_PASS or USER_PASS != CONFIRM_PASS:
                USER_PASS = input("Enter your password: ")
                CONFIRM_PASS = input("Confirm your password: ")

            P_SALT = urandom(32)
            TO_BE_HASHED = USER_PASS.encode() + P_SALT
            P_HASH = sha3_512(TO_BE_HASHED).hexdigest()
            C.execute("INSERT INTO users VALUES (?, ?, ?)", (USER_NAME, P_HASH, P_SALT))
            del USER_PASS, CONFIRM_PASS, TO_BE_HASHED

        else: #RESP == 'n'
            print("Goodbye")

    else: #There was a record with a matching username
        USER_PASS = input("Enter your password: ")
        C.execute("SELECT * FROM users where user_name=?", (USER_NAME,))
        RESULT = C.fetchone() #Fetch the user's record from the db
        TO_BE_HASHED = USER_PASS.encode() + RESULT[2] #Result[2] is the user salt

        if RESULT[1] == sha3_512(TO_BE_HASHED).hexdigest():
            print("Login Success!")
        else:
            print("Login fail.")
        del USER_PASS, TO_BE_HASHED

    CONN.commit()
    CONN.close()
