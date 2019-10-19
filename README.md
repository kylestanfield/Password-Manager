# Password-Manager

Local command line based password manager written in Python. This script features a login system, salting and hashing with SHA2_512, password encryption and authentication with AES, PBKDF2, as well as databases implemented with SQLite. Mostly follows standards set in RFC8018.


## Prerequisites

You must have python3 and the PyCrypto module installed. If you have pip, this is extremely simple:
```
pip install pycrypto
```

## Getting Started

Simply clone this repo and run 
```python3 manager.py``` 
to get started.

A simple interaction with the program will procede as follows:

First, create your account and password
```
python3 manager.py -a kyle ElPsyKongroo
```
Then you will be prompted to add new accounts to the password manager:
```
Enter a to add a new record, or q to quit: a
Enter the website name: github.com
Enter your username for the site: OpaKyleStyle
Enter your password for the site: NeverGonnaCacheMe
```
Next, the manager will show you all available accounts, and you can choose which to view:
```
0 github.com

Enter the index of the record you would like to view, a to add a new record, or q to quit: 0

 github.com OpaKyleStyle NeverGonnaCacheMe 

Enter u to update this record, d to delete this record, v to view another record, or q to quit: q
```

## License

This project is licensed under the GNU General Public License 3.0 - see the [LICENSE](LICENSE) file for details
