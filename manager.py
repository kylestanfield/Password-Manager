#!/usr/bin/env python3
"""Command-line based password manager utility."""

import encrypt
import sqlite3
import sys

def strip(input):
    """Strip a string of all characters not in [a-zA-Z0-9_!-)]."""
    return ''.join(chr for chr in input if chr.isalnum() or chr in '._!@#$%^&*()')

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

    CONN = sqlite3.connect('users/' + input_user + '.db')
    C = CONN.cursor()
    C.execute("CREATE TABLE IF NOT EXISTS sites (website text, user_name text, pass_cipher text, pass_salt text, initialization_vector, MAC text, MAC_salt text)")

    #Get all user websites, show the names, and then get user input
    user_input = ' ' #PLACEHOLDER UNTIL USER ISSUES COMMAND
    while user_input != 'q':
            sites = []
            for i, row in enumerate(C.execute("SELECT * FROM sites")):
                print(i, row[0])
                sites.append(row)

            index = int(input("Enter the index of the record you would like to view:\n"))
            #TODO: ADD ERROR CHECKING HERE, FOR NON-INTEGER AND OUT OF RANGE
            site = sites[index][0]
            print(sites[index]) #TODO: user only needs to see website, user_name, and pass
            #TODO: unencrypt the pass_cipher and show to user

            user_input = input("Enter a to view another record, u to update this record, d to delete this record, or q to quit: ")
            if user_input == 'q':
                pass

            elif user_input == 'a':
                pass

            elif user_input == 'u':
                u_name = strip(input("Enter your new username (or blank to keep it the same): "))
                if not u_name:
                    u_name = sites[index][1]
                u_pass = strip(input("Enter your new password: "))
                #Going to need to update pass_cipher, pass_salt, IV, MAC, MAC_SALT
                new_salt = encrypt.generate_salt()
                new_iv = encrypt.generate_initialization_vector()
                new_cipher = encrypt.encrypt_text(u_pass, encrypt.generate_key(u_pass, new_salt), new_iv)
                new_mac_salt = encrypt.generate_salt()
                mac_key = encrypt.generate_key(u_pass, new_mac_salt)
                new_mac = generate_mac(mac_key, new_cipher)
                C.execute("UPDATE sites SET user_name = ?, pass_cipher = ?, pass_salt = ?, initialization_vector = ?, MAC = ?, MAC_salt = ? WHERE website = ?", (u_name, new_cipher, new_salt, new_iv, new_mac, new_mac_salt, site,))

            elif user_input == 'd':
                C.execute("DELETE FROM sites WHERE website = ?", (site,))
 
    CONN.commit()
    CONN.close()
