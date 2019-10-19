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
    if argc < 3 or argc > 4 or (argc == 4 and args[1] != '-a') or (argc == 3 and args[1] == '-a'):
        print("Usage: python manager.py [-a] $USER $PASS")
        sys.exit()

    CONN = sqlite3.connect('users.db')
    C = CONN.cursor()
    C.execute("CREATE TABLE IF NOT EXISTS users (user_name text, pass_hash text, salt text)")


    input_user = strip(args[argc-2])
    input_pass = strip(args[argc-1]).encode('utf-8')
    
    C.execute("SELECT * FROM users WHERE user_name=?", (input_user,))
    data = C.fetchone()

    if not data: #If the SQL command returns nothing
        if argc > 3: #User gave -a
            s = encrypt.generate_salt()
            new_data = (input_user, encrypt.generate_mac(encrypt.generate_key(input_pass, s),
                                                         input_pass), s,)

            C.execute("INSERT INTO users VALUES (?,?,?)", new_data)

        else:
            print("That user does not exist!")
            CONN.commit()
            CONN.close()
            sys.exit(1)

    else:
        if argc > 3:
            print("That user already exists!")
            CONN.commit()
            CONN.close()
            sys.exit(1)

        else:
            salt = data[2]
            derived_mac = encrypt.generate_key(input_pass, salt)
            if not encrypt.verify_mac(derived_mac, input_pass, data[1]):
                print("Incorrect password, loser.")
                CONN.commit()
                CONN.close()
                sys.exit(1)

            print("Login successful.")

    CONN.commit()
    CONN.close()

    CONN = sqlite3.connect('users/' + input_user + '.db')
    C = CONN.cursor()
    C.execute("CREATE TABLE IF NOT EXISTS sites (website text, user_name text,"
              "pass_cipher text, pass_salt text, initialization_vector, MAC text, MAC_salt text)")

    #Get all user websites, show the names, and then get user input
    user_input = ' ' #PLACEHOLDER UNTIL USER ISSUES COMMAND

    while user_input != 'q':
            websites = []
            num_records = 0
            C.execute("SELECT * FROM sites")
            for i, row in enumerate(C.fetchall()):
                print(i, row[0])
                websites.append(row)
                num_records += 1
            print()

            if num_records > 0:
                index = strip(input("Enter the index of the record you would"
                                    " like to view, a to add a new record, or"
                                    " q to quit: "))
            else:
                index = strip(input("Enter a to add a new record, or q to quit:\n"))

            if index == 'a':
                site = strip(input("Enter the website name: "))
                u_name = strip(input("Enter your username for the site: "))
                u_pass = strip(input("Enter your password for the site: ")).encode('utf-8')

                pass_salt = encrypt.generate_salt()
                derived_key = encrypt.generate_key(input_pass, pass_salt)
                iv = encrypt.generate_initialization_vector()
                cipher = encrypt.encrypt_text(u_pass, derived_key, iv)

                mac_salt = encrypt.generate_salt()
                mac_key = encrypt.generate_key(input_pass, mac_salt)
                mac = encrypt.generate_mac(mac_key, cipher)

                C.execute("INSERT INTO sites VALUES (?, ?, ?, ?, ?, ?, ?)", (site, u_name, cipher,
                           pass_salt, iv, mac, mac_salt,))
                print('\n')
            elif index == 'q':
                user_input = 'q'                
            else:
                try: 
                    index = int(index)
                except ValueError:
                    print("That's not an integer!")
                    CONN.commit()
                    CONN.close()
                    sys.exit(1)

                if index >= num_records or index < 0:
                    print("What are you trying to pull, Mr? That index is out of range.")
                    CONN.commit()
                    CONN.close()
                    sys.exit(1)

                #Extract the data from the website tuple
                record = websites[index]
                site = record[0]
                site_user = record[1]
                cipher_text = record[2]
                pass_salt = record[3]
                iv = record[4]
                
                print('\n', site, site_user, encrypt.decrypt_text(cipher_text, 
                      encrypt.generate_key(input_pass, pass_salt), iv).decode('utf-8'), '\n')

                user_input = input("Enter u to update this record,"
                             " d to delete this record, v to view"
                             " another record, or q to quit: ")

                if user_input == 'q':
                    pass

                elif user_input == 'u':
                    u_name = strip(input("Enter your new username "
                                         "(or blank to keep it the same): "))

                    if not u_name:
                        u_name = websites[index][1]

                    u_pass = strip(input("Enter your new password: ")).encode('utf-8')

                    #Going to need to update pass_cipher, pass_salt, IV, MAC, MAC_SALT

                    new_salt = encrypt.generate_salt()
                    new_iv = encrypt.generate_initialization_vector()
                    new_cipher = encrypt.encrypt_text(u_pass, 
                                    encrypt.generate_key(input_pass, new_salt), new_iv)

                    new_mac_salt = encrypt.generate_salt()
                    mac_key = encrypt.generate_key(input_pass, new_mac_salt)
                    new_mac = encrypt.generate_mac(mac_key, new_cipher)

                    C.execute("UPDATE sites SET user_name = ?, pass_cipher = ?,"
                              "pass_salt = ?, initialization_vector = ?,"
                              "MAC = ?, MAC_salt = ? WHERE website = ?",
                              (u_name, new_cipher, new_salt,
                               new_iv, new_mac, new_mac_salt, site,))

                    print()
                elif user_input == 'd':
                    C.execute("DELETE FROM sites WHERE website = ?", (site,))
 
    CONN.commit()
    CONN.close()
