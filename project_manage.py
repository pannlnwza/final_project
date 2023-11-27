from database import DB, Table, CSVReader
import sys
import csv


def initializing():
    db = DB()

    # persons table
    persons_csv = CSVReader('persons.csv')
    read_persons = persons_csv.read_csv()
    persons_table = Table('persons', read_persons)
    db.insert(persons_table)

    # login table
    login_csv = CSVReader('login.csv')
    read_login = login_csv.read_csv()
    login_table = Table('login', read_login)
    db.insert(login_table)

    return db


def login():
    username = input('Enter your username: ')
    password = input('Enter your password: ')

    db = initializing()
    login_table = db.search('login')

    for person in login_table.table:
        if person['username'] == username and person['password'] == password:
            return [person["ID"], person["role"]]

    return None


def exit():
    data = database.get_tables()

    for table_name, table in data.items():
        file_name = f'{table_name}.csv'
        file = open(file_name, 'w', newline='')
        writer = csv.writer(file)

        writer.writerow(table.table[0].keys())

        for row in table.table:
            writer.writerow(row.values())

    print("Exiting the program.")
    sys.exit()


db = DB()
database = initializing()
db.insert(database)
print()
val = login()
if val is None:
    print('Your username or password is invalid.')
else:
    print(val)
print()


# END part 1

# CONTINUE to part 2 (to be done for the next due date)

# based on the return value for login, activate the code that performs activities according to the role defined for that person_id

# if val[1] = 'admin':
    # do admin related activities
# elif val[1] = 'advisor':
    # do advisor related activities
# elif val[1] = 'lead':
    # do lead related activities
# elif val[1] = 'member':
    # do member related activities
# elif val[1] = 'faculty':
    # do faculty related activities

exit()

