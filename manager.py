"""Command-line based password manager utility."""
import hashlib
import sqlite3

if __name__ == '__main__':
    USER_NAME = input("Enter your user name: ")
    CONN = sqlite3.connect('users.db')
    C = CONN.cursor()
    C.execute("CREATE TABLE IF NOT EXISTS users (user_name text, pass_hash text)")
    C.execute("SELECT * FROM users where user_name=?", (USER_NAME,))
    if not C.fetchone(): #If the username isn't in the Database
        RESP = ''
        while RESP not in ('y', 'n'):
            RESP = input("User name not found." +
                         " Create a new user? (Y/N): ").lower()

        if RESP == 'y':
            USER_PASS = input("Enter your password: ")
            CONFIRM_PASS = ''
            while USER_PASS and CONFIRM_PASS != USER_PASS:
                CONFIRM_PASS = input("Confirm your password: ")
                if CONFIRM_PASS != USER_PASS:
                    USER_PASS = ("Re-enter your password: ")

            P_HASH = hashlib.sha256(str.encode(USER_PASS)).hexdigest()
            C.execute("INSERT INTO users VALUES (?, ?)", (USER_NAME, P_HASH))
            del USER_PASS, CONFIRM_PASS
        else:
            print("Goodbye")

    else: #There was a record with a matching username
        USER_PASS = input("Enter your password: ")
        C.execute("SELECT * FROM users where user_name=?", (USER_NAME,))
        if C.fetchone()[1] == hashlib.sha256(str.encode(USER_PASS)).hexdigest():
            print("Login Success!") #DEBUG
        else:
            print("Login fail.") #dEBUG
        del USER_PASS

    CONN.commit()
    CONN.close()
