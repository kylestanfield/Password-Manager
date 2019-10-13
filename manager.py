#!/usr/bin/env python3
"""Command-line based password manager utility."""

import encrypt
import sqlite3
import sys

def strip(input):
    """Strip a string of all characters not in [a-zA-Z0-9_!-)]."""
    return ''.join(chr for chr in input if chr.isalnum() or chr in '_!@#$%^&*()')

if __name__ == '__main__':

    args = sys.argv
    argc = len(args)
    if argc < 3 or argc > 4 or (argc == 4 and args[1] != '-a'):
        print("Usage: python manager.py [-a] $USER $PASS")
        sys.exit()

    CONN = sqlite3.connect('users.db')
    C = CONN.cursor()
    C.execute("CREATE TABLE IF NOT EXISTS users (user_name text, pass_hash text, salt text)")

    input_user = ''
    input_pass = ''

    if argc == 3:
        input_user = strip(args[1])
        input_pass = strip(args[2])
    else:
        input_user = strip(args[2])
        input_pass = strip(args[3])
    
    input_pass = input_pass.encode('utf-8')

    C.execute("SELECT * FROM users WHERE user_name=?", (input_user,))
    data = C.fetchone()
    if not data:
        if argc > 3: #User gave -a
            s = encrypt.generate_salt()
            new_data = (input_user, encrypt.generate_mac(encrypt.generate_key(input_pass, s),input_pass), s,)
            C.execute("INSERT INTO users VALUES (?,?,?)", new_data)
        else:
            print("That user does not exist!")
            sys.exit()
    else:
        if argc > 3:
            print("That user already exists!")
            sys.exit()
        else:
            if not encrypt.verify_mac(encrypt.generate_key(input_pass, data[2]), input_pass, data[1]):
                print("Incorrect password, loser.")
                sys.exit()
            else:
                print("Login successful.")

    CONN.commit()
    CONN.close()
    
