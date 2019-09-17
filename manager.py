"""Command-line based password manager utility."""
import hashlib
import sqlite3

user_name = raw_input("Enter your user name: ")
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_name text, pass_hash text)")
c.execute("SELECT * FROM users where user_name=?", (user_name,))
if not c.fetchone(): #If the username isn't in the Database
    resp = ''
    while resp != 'y' and resp != 'n':
        resp = raw_input("User name not found." +
            " Create a new user? (Y/N): ").lower()
    if resp == 'y':
        user_pass = raw_input("Enter your password: ")
        confirm_pass = ''
        while user_pass and confirm_pass != user_pass:
            confirm_pass = raw_input("Confirm your password: ")
            if confirm_pass != user_pass:
                user_pass = ("Re-enter your password: ")

        hash = hashlib.sha256(str.encode(user_pass)).hexdigest()
        c.execute("INSERT INTO users VALUES (?, ?)", (user_name, hash))
        del user_pass, confirm_pass
    else:
        print("Goodbye")
else: #There was a record with a matching username
    user_pass = raw_input("Enter your password: ")
    c.execute("SELECT * FROM users where user_name=?", (user_name,))
    if c.fetchone()[1] == hashlib.sha256(str.encode(user_pass)).hexdigest():
        print("Login Success!") #DEBUG
    else:
        print("Login fail.")
    del user_pass
conn.commit()
conn.close()
