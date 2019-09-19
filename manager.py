#!/usr/bin/env python3
"""Command-line based password manager utility."""

from Crypto.Cipher import AES
from hashlib import sha3_512
import sqlite3
from os import urandom

def strip(input):
    return ''.join(chr for chr in input if chr.isalnum() or chr == '_')

if __name__ == '__main__':
    USER_NAME = input("Enter your user name: ")
    CONN = sqlite3.connect('users.db')
    C = CONN.cursor()
    C.execute("CREATE TABLE IF NOT EXISTS users (user_name text, pass_hash text, salt text, db_iv text)")
    C.execute("SELECT * FROM users where user_name=?", (USER_NAME,))

    if not C.fetchone(): #If the username isn't in the database
        RESP = ''
        while RESP not in ('y', 'n'):
            RESP = input("User name not found." +
                         " Create a new user? (Y/N): ").lower()

        if RESP == 'y': #Get the user's password and add them to the database
            USER_PASS = ''
            CONFIRM_PASS = ''
            while not USER_PASS or USER_PASS != CONFIRM_PASS:
                USER_PASS = input("Enter your password: ")
                CONFIRM_PASS = input("Confirm your password: ")

            #Add a random 32 byte salt to the password to make the hash more secure
            P_SALT = urandom(32)
            P_HASH = sha3_512(USER_PASS.encode() + P_SALT).hexdigest()
            C.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (USER_NAME, P_HASH, P_SALT, ''))
            del USER_PASS, CONFIRM_PASS

        else: #RESP == 'n'
            print("Goodbye")

    else: #There was a record with a matching username
        USER_PASS = input("Enter your password: ")
        C.execute("SELECT * FROM users where user_name=?", (USER_NAME,))
        RESULT = C.fetchone() #Fetch the user's record from the db

        if RESULT[1] == sha3_512(USER_PASS.encode() + RESULT[2]).hexdigest():
            #Login Success
            CONN2 = sqlite3.connect('users/' + USER_NAME + '.db')
            CURSOR2 = CONN2.cursor()
            CURSOR2.execute("CREATE TABLE IF NOT EXISTS ? (site text, user text, pass text)",USER_NAME)
            #The above line of code does not work
        else:
            #Login fail.
            pass
        del USER_PASS

    CONN.commit()
    CONN.close()
