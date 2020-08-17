import random
import sqlite3

# Connect to a database
conn = sqlite3.connect('card.s3db')
# Creates a cursor
cur = conn.cursor()
# Creates table
cur.execute("""
    CREATE TABLE IF NOT EXISTS card(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
    )
""")
conn.commit()
# Testing
tester = None


def random_word(n):
    temp = []
    for x in range(n):  # generates nine digits
        temp.append(str(random.randint(0, 9)))
    return ''.join(temp)


def find_in_database(acc, pw):
    global accounts
    global tester
    cur.execute(f"SELECT * FROM card WHERE {acc}=number AND {pw}=pin")
    tester = cur.fetchone()
    return False if tester is None else True


def selection(a):
    if a == 1:
        return input('''
1. Create an account
2. Log into account
0. Exit
''')
    return input('''
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
''')


def checksum(e):
    total = 0
    acc_num = []
    for x in range(15):
        acc_num.append(int(e[x]))
    for x in range(0, 16, 2):
        acc_num[x] *= 2
    for x in acc_num:
        if x > 9:
            x -= 9
        total += x
    if total % 10 == 0:
        return '0'
    else:
        return str((total // 10 + 1) * 10 - total)


def do_transaction(amount, account):
    cur.execute("SELECT number,balance FROM card")
    checker = cur.fetchall()
    for i in range(len(checker)):
        if checker[i][0] == account:
            checker[i] = list(checker[i])
            checker[i][1] += amount
            cur.execute(f"UPDATE card set balance={checker[i][1]} WHERE number={account}")
            conn.commit()
            return True
    return False


cur.execute("SELECT id,number,pin,balance FROM card")
accounts = cur.fetchall()
choice = selection(1)
while choice != '0':
    if choice == '1':
        print('''
Your card has been created
Your card number:''')
        account_num = f'400000{random_word(9)}'
        account_num = account_num + checksum(account_num)
        print(account_num)
        print('Your card PIN:')
        pswd = random_word(4)
        print(pswd)
        # Inserts record into table
        cur.execute(f"INSERT INTO card(number,pin) VALUES({account_num},{pswd})")
        conn.commit()
        choice = selection(1)
    if choice == '2':
        num = input('\nEnter your card number:\n')
        pin = input('Enter your PIN:\n')
        if find_in_database(num, pin):
            print('\nYou have successfully logged in!')
            choice2 = selection(2)
            while choice2 != '0':
                if choice2 == '1':  # Balance
                    print(f"\nBalance: {tester[3]}")
                    choice2 = selection(2)
                elif choice2 == '2':  # Add income
                    tester = list(tester)  # tuple is immutable
                    tester[3] += int(input('\nEnter income:\n'))
                    tester = tuple(tester)
                    cur.execute(f"UPDATE card SET balance = {tester[3]} WHERE id = {tester[0]}")
                    conn.commit()
                    print('Income was added!')
                    choice2 = selection(2)
                elif choice2 == '3':
                    transfer = input('\nTransfer\nEnter card number:\n')
                    # check the card num with Lunh
                    if checksum(transfer[0:15]) != transfer[15]:
                        print('Probably you made mistake in the card number. Please try again!\n')
                        choice2 = selection(2)
                    elif not do_transaction(0, transfer):  # returns false when card doesnt exists
                        print('Such a card does not exist.')
                        choice2 = selection(2)
                    elif num == transfer:
                        print("You can't transfer money to the same account!")
                        choice2 = selection(2)
                    else:  # does transfer
                        money_transfer = int(input('Enter how much money you want to transfer:\n'))
                        if money_transfer <= tester[3]:
                            do_transaction(money_transfer, transfer)
                            tester = list(tester)
                            tester[3] -= money_transfer
                            cur.execute(f"UPDATE card SET balance = {tester[3]} WHERE id = {tester[0]}")
                            # updates receiver's account
                            cur.execute(f"SELECT * FROM card WHERE {transfer}=number")
                            receiver = list(cur.fetchone())
                            new_balance = receiver[3]
                            cur.execute(f"UPDATE card SET balance = {new_balance} WHERE number = {receiver[1]}")
                            conn.commit()
                            print('Success!')
                            choice2 = selection(2)
                        else:
                            print('Not enough money!')
                            choice2 = selection(2)
                elif choice2 == '4':  # Close account
                    cur.execute(f"DELETE FROM card WHERE id={tester[0]}")
                    conn.commit()
                    print('\nThe account has been closed!')
                    choice = selection(1)
                    break
                elif choice2 == '5':  # Log out
                    print('\nYou have successfully logged out!')
                    print('\nBye!')
                    quit()
            if choice2 == '0':
                print('Bye!')
                quit()
        else:
            print('\nWrong card number or PIN!')
            choice = selection(1)
    if choice == '0':
        print('\nBye!')
        quit()
