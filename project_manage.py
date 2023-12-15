from database import DB, Table, CSVReader
import sys
import csv
import random
from datetime import datetime


class User:
    def __init__(self, uid, username, role):
        self.id = uid
        self.user = username
        self.role = role

    def see_invitaion_req(self):
        for i in main_db.search('member_request').table:
            if self.id == i['to_be_member']:
                print(main_db.search('member_request').filter(lambda x: x['to_be_member'] == self.id))
            else:
                print("You don't have any invitations yet.")

    def respond_invitation(self, choice, project_id):
        num_member = ''
        if choice.lower() == 'accept':
            for i in main_db.search('project_table').filter(lambda x: x['ProjectID'] == self.id).table:
                if i['Member1'] == 'None':
                    num_member = 'Member1'
                elif i['Member1'] != 'None':
                    num_member = 'Member2'
                else:
                    print('This group is already full.')
                    sys.exit()
            main_db.search('member_request').update('to_be_member', self.id, 'Response', 'Accepted')
            main_db.search('login_table').update('ID', self.id, 'role', 'member')
            main_db.search('project_table').update('ProjectID', project_id, num_member, self.id)  # num represent a Member1 or 2
            self.role = 'member'
        elif choice.lower() == 'deny':
            main_db.search('member_request').update('ProjectID', project_id, 'Response', 'Denied')

    def create_project(self):
        project_title = input("Enter your project title: ")
        main_db.search('login_table').update('ID', self.id, 'role', 'lead')
        print(main_db.search('login_table'))
        project_id = ''
        self.role = 'lead'
        for i in range(6):
            num = str(random.randint(0, 9))
            project_id += num
        return int(project_id), project_title


class Member(User):
    def __init__(self, uid, username, role, project_id):
        super().__init__(uid, username, role)
        self.id = uid
        self.user = username
        self.role = role
        self.project_id = project_id

    def see_project_detail(self):
        print(main_db.search('project_table').filter(lambda x: x['ProjectID'] == self.project_id))

    def see_group_pending_invites(self):
        print(main_db.search('member_request').filter(lambda x: x['ProjectID'] == self.project_id))

class Lead(User):
    def __init__(self, uid, username, role, project_id):
        super().__init__(uid, username, role)
        if role != 'lead':
            raise ValueError('You need be be a project lead to use these functions.')
        self.id = uid
        self.user = username
        self.role = role
        self.project_id = project_id

    def see_status(self):
        print(main_db.search('project_table').filter(lambda x: x['ProjectID'] == self.project_id))

    def send_invite_to_member(self):
        for project in main_db.search('project_table').filter(lambda x: x['ProjectID'] == self.project_id).table:
            if project['Member1'] == 'None' or project['Member2'] == 'None':
                print('List of students: ')
                print(main_db.search('login_table').filter(lambda x: x['role'] == 'student'))

                new_member_id = int(input('Who do you want to invite?(ID): '))
                for req in main_db.search('member_request').table:
                    if project['Member1'] != 'None' and project['Member2'] != 'None':
                        print('Your group is already full.')
                        return
                    if req['to_be_member'] == new_member_id:
                        print('You already sent an invitation to this student.')
                        return

        invitation_dict = {'ProjectID': self.project_id,
                           'to_be_member': new_member_id,
                           'Response': 'pending',
                           'Response_date': datetime.now()}
        main_db.search('member_pending').insert_table(invitation_dict)
        print(main_db.search('member_pending'))

    # def send_req_to_advisor(self):
    #     for i in main_db.search('project_table').filter(lambda x: x['ProjectID'] == self.id).table:  # check if group still avarible
    #         if i['Advisor'] != 'None':
    #             print('Your group is full')
    #         elif i['Advisor'] == 'None':
    #             print(data2.search('login').filter(lambda x: x['role'] == 'faculty'))
    #             fc_want = int(input('who is faculty you want to invite(id): '))
    #             for i in data2.search('advisor_pending').table:
    #                 if i['to_be_advisor'] == fc_want:
    #                     print('you already sent an invitation')
    #             dict_ad = {'ProjectID': self.id, 'to_be_advisor': fc_want, 'Response': 'pending',
    #                        'Response_date': '11/11'}
    #             data2.search('advisor_pending').insert_row(dict_ad)
    #             print(data2.search('advisor_pending'))


class Faculty(User):
    def __init__(self, uid, username, role):
        super().__init__(uid, username, role)
        self.id = uid
        self.user = username
        self.role = role

    def advisor_pending_req(self):
        for req in main_db.search('advisor_request').table:
            if self.id == req['to_be_advisor']:
                print(main_db.search('advisor_request').filter(lambda x: x['to_be_advisor'] == self.id))
            elif self.id != req['to_be_advisor']:
                print("You don't have any pending request.")

    def advisor_respond_req(self, choice, project_id):
        pending_req = main_db.search('advisor_request').filter(lambda x: x['ProjectID'] == project_id).table
        if self.id != pending_req['to_be_advisor']:
            print('You are not invited to be an advisor for this group.')
        elif self.id == pending_req['to_be_advisor']:
            if choice.lower() == 'accept':
                main_db.search('advisor_request').update('ProjectID', project_id, 'Response', 'Accepted')
                main_db.search('login_table').update('ID', self.id, 'role', 'advisor')
                main_db.search('project_table').update('ProjectID', project_id, 'Advisor', self.id)
            elif choice.lower() == 'deny':
                main_db.search('advisor_request').update('ProjectID', 'project_id', 'Response', 'Denied')

    def see_all_projects_details(self):
        print(main_db.search('project_table'))


class Advisor(User):
    def __init__(self, uid, username, role, project_id):
        super().__init__(uid, username, role)
        self.id = uid
        self.user = username
        self.role = role
        self.project_id = project_id

    def update_status(self):
        status = input('Update the project status: ')
        main_db.search('project_table').update('ProjectID', self.project_id, 'status', status)
        print('Project Status Updated.')

    def see_project_detail(self):
        print(main_db.search('project_table').filter(lambda x: x['ProjectID'] == self.id))

    def approval(self, choice):
        if choice.lower() == 'yes':
            main_db.search('project_table').update('ProjectID', self.id, 'status', 'approved')
        elif choice.lower() == 'no':
            main_db.search('project_table').update('ProjectID', self.id, 'status', 'disapproved')


def initializing():
    db = DB()
    persons_csv = CSVReader('persons.csv').read_csv()
    persons_table = Table('persons', persons_csv)
    db.insert(persons_table)

    project_table = Table('project', [])
    db.insert(project_table)

    advisor_pending_request_table = Table('advisor_request', [])
    db.insert(advisor_pending_request_table)

    member_pending_request_table = Table('member_request', [])
    db.insert(member_pending_request_table)
    return db


def login():
    db = initializing()
    login_table = db.search('login')
    if login_table:
        while True:
            username = input('Enter your username: ')
            password = input('Enter your password: ')
            for person in login_table.table:
                if person['username'] == username and person['password'] == password:
                    print(f'Welcome to the Program, {username}')
                    print()
                    return [person['username'], person['role']]
            print('Invalid username or password. Please try again.')
            print()
    else:
        return None


# def exit():
#     data = database.get_tables()
#
#     for table_name, _table in data.items():
#         file_name = f'{table_name}.csv'
#         file = open(file_name, 'w', newline='')
#         writer = csv.writer(file)
#
#         writer.writerow(_table.table[0].keys())
#
#         for row in _table.table:
#             writer.writerow(row.values())
#
#     print("Exiting the program.")
#     sys.exit()


main_db = initializing()

print()
val = login()
login_table = main_db.search('login')
user_role = login_table.filter(lambda x: x['username'] == val[0]).select('role')
user = User(val[0], val[1], user_role[0]['role'])



# END part 1

# CONTINUE to part 2 (to be done for the next due date)

# based on the return value for login, activate the code that performs activities according to the role defined for that person_id

# if logged_in['role'] == 'admin':
#     while True:
#         print(f'User: {logged_in["username"]} (ID: {logged_in["ID"]})')
#         print(f'Choose function for admin: ')
#         print('1. See all project information')
#         print("2. See all student that didn't join any project")
#         print("3. See all faculty that didn't advise any project")
#         print('4. See all advisor pending request')
#         print('0. Exit the program')
#         choice = int(input("Enter your choice: "))
#         if choice == 1:
#             pass
#         if choice == 2:
#             pass
#         if choice == 3:
#             pass
#         if choice == 4:
#             pass
#         elif choice == 0:
#             print('Exiting the program.')
#             break
#         else:
#             print('Invalid choice. Please choose the valid choices (1,2,3,4 and 0)')
# elif logged_in['role'] == 'student':
#     while True:
#         print(f'User: {logged_in["username"]} (ID: {logged_in["ID"]})')
#         print(f'Choose function for student: ')
#         print('1. See project invitations')
#         print("2. Create a project")
#         print('0. Exit the program')
#         choice = int(input("Enter your choice: "))
#         if choice == 1:
#             pass
#         if choice == 2:
#             pass
#         elif choice == 0:
#             print('Exiting the program.')
#             break
#         else:
#             print('Invalid choice. Please choose the valid choices (1,2 and 0)')

# elif val[1] = 'advisor':
#     do advisor related activities
# elif val[1] = 'lead':
#     do lead related activities
# elif val[1] = 'member':
#     do member related activities
# elif val[1] = 'faculty':
#     do faculty related activities

# exit()



