from database import DB, Table, CSVReader
import csv
import sys
import random
from datetime import datetime


class Student:
    def __init__(self, uid, username, role):
        self.id = uid
        self.user = username
        self.role = role

    def see_invitation_req(self):
        n = 0
        for i in member_pending.table:
            if self.id == i['to_be_member']:
                print(member_pending.filter(lambda x: x['to_be_member'] == self.id))
                n += 1
        if n == 0:
            print("You don't have any invitations yet")

    def respond_invitation(self, choice, project_id):
        if choice.lower() == 'accept':
            for i in project_table.filter(lambda x: x['ProjectID'] == project_id).table:
                if i['Member1'] == '-':
                    project_table.update('ProjectID', project_id, 'Member1', '-', 'Member1', self.id)
                elif i['Member1'] != '-' and i['Member2'] == '-':
                    project_table.update('ProjectID', project_id, 'Member2', '-', 'Member2', self.id)
                else:
                    print('This group is already full')
                    return
            member_pending.update('ProjectID', project_id, 'to_be_member', self.id, 'Response', 'Accepted')
            member_pending.update('ProjectID', project_id, 'to_be_member', self.id, 'Response_date', datetime.now())
            save('member_pending_request')
            login_table.update('ID', self.id, 'username', self.user, 'role', 'member')
            save('login')
            save('project')
            self.role = 'member'
            print(f'You have successfully joined the group ({project_id})')
            print(f'Logging out. The program has to log out because the role changed.')
            sys.exit()
        elif choice.lower() == 'deny':
            member_pending.update('ProjectID', project_id, 'to_be_member', self.id, 'Response', 'Denied')
            member_pending.update('ProjectID', project_id, 'to_be_member', self.id, 'Response_date', datetime.now())
            save('member_pending_request')
            print(f'You have denied the invitation')

    def create_project(self):
        project_title = input("Enter your project title: ")
        login_table.update('ID', self.id, 'username', self.user, 'role', 'lead')
        save('login')
        project_id = ''
        self.role = 'lead'
        for i in range(6):
            num = str(random.randint(0, 9))
            project_id += num
        project = {'ProjectID': project_id,
                   'Title': project_title,
                   'Lead': self.id,
                   'Member1': '-',
                   'Member2': '-',
                   'Advisor': '-',
                   'Status': 'Processing',
                   'Evaluator': '-',
                   'Result': '-',
                   'Feedback': '-',
                   'Approval': '-'}
        project_table.table.append(project)
        save('project')
        print('You have successfully created a project.')
        print(f'Logging out. The program has to log out because the role changed.')
        sys.exit()


class Member:
    def __init__(self, uid, username, role, project_id):
        self.id = uid
        self.user = username
        self.role = role
        self.project_id = project_id

    def see_project_detail(self):
        print(project_table.filter(lambda x: x['ProjectID'] == self.project_id))

    def see_group_pending_invites(self):
        member_invites = member_pending.filter(lambda x: x['ProjectID'] == self.project_id)
        advisor_invites = advisor_pending.filter(lambda x: x['ProjectID'] == self.project_id)
        if member_invites or advisor_invites:
            print(member_invites)
            print(advisor_invites)
        else:
            print('There is not invitation sent.')


class Lead:
    def __init__(self, uid, username, role, project_id):
        if role != 'lead':
            raise ValueError('You need be be a project lead to use these functions.')
        self.id = uid
        self.user = username
        self.role = role
        self.project_id = project_id

    def see_detail(self):
        print(project_table.filter(lambda x: x['ProjectID'] == self.project_id))

    def send_invite_to_student(self):
        new_member_id = int(input('Who do you want to invite?(ID): '))
        for project in project_table.filter(lambda x: x['ProjectID'] == self.project_id).table:
            if project['Member1'] == '-' or project['Member2'] == '-':
                invitation_dict = {'ProjectID': self.project_id,
                                   'to_be_member': new_member_id,
                                   'Response': 'Pending',
                                   'Response_date': '-'}
                member_pending.insert_table(invitation_dict)
                print(f'An invitation has been sent to user {new_member_id} (student).')
                save('member_pending_request')
                return

            for req in member_pending.table:
                if project['Member1'] != '-' and project['Member2'] != '-':
                    print('Your group is already full.')
                    return
                if req['to_be_member'] == new_member_id:
                    print('You already sent an invitation to this student.')
                    return

    def send_req_to_advisor(self):
        for i in project_table.filter(lambda x: x['ProjectID'] == self.project_id).table:
            if i['Advisor'] != '-':
                print('Your group already has an advisor.')
            elif i['Advisor'] == '-':
                faculty_id = input('Who do you want to invite(faculty)? (ID): ')
                for req in advisor_pending.table:
                    if req['to_be_advisor'] == faculty_id:
                        print('You already sent an invitation to this person')
                invitation_dict = {'ProjectID': self.project_id,
                                   'to_be_advisor': faculty_id,
                                   'Response': 'Pending',
                                   'Response_date': '-'}
                advisor_pending.insert_table(invitation_dict)
                save('advisor_pending_request')
                print(f'An invitation has been sent to user {faculty_id} (faculty).')

    def send_project(self):
        choice = input('Do you want to send the project? (Y/N): ')
        if choice.lower() == 'y':
            project_table.update2('ProjectID', self.project_id, 'Status', 'sent')
            save('project')
            print('You sent the project.')
        elif choice.lower() == 'n':
            pass

    def see_eval_result(self):
        result = project_table.filter(lambda x: x['ProjectID'] == self.project_id).select('Result')
        if result[0]['Result'] != '-':
            print('Evaluation results:')
            evaluator = project_table.filter(lambda x: x['ProjectID'] == self.project_id).select('Evaluator')
            result = project_table.filter(lambda x: x['ProjectID'] == self.project_id).select('Result')
            feedback = project_table.filter(lambda x: x['ProjectID'] == self.project_id).select('Feedback')
            print(f'Evaluator: {evaluator[0]["Evaluator"]}\n'
                  f'Result: {result[0]["Result"]}\n'
                  f'Feedback: {feedback[0]["Feedback"]}')
        else:
            print("Your project hasn't been evaluated yet.")


class Faculty:
    def __init__(self, uid, username, role):
        self.id = uid
        self.user = username
        self.role = role

    def advisor_pending_req(self):
        n = 0
        for req in advisor_pending.table:
            if self.id == req['to_be_advisor']:
                print(advisor_pending.filter(lambda x: x['to_be_advisor'] == self.id))
                n += 1
        if n == 0:
            print("You don't have any invitations yet.")

    def advisor_respond_req(self, choice, project_id):
        if choice.lower() == 'accept':
            for i in project_table.filter(lambda x: x['ProjectID'] == project_id).table:
                if i['Advisor'] == '-':
                    project_table.update('ProjectID', project_id, 'Advisor', '-', 'Advisor', self.id)
                    save('project')
                    advisor_pending.update('ProjectID', project_id, 'to_be_advisor', self.id, 'Response', 'Accepted')
                    advisor_pending.update('ProjectID', project_id, 'to_be_advisor', self.id, 'Response_date', datetime.now())
                    save('advisor_pending_request')
                    login_table.update('ID', self.id, 'username', self.user, 'role', 'advisor')
                    save('login')
                    self.role = 'advisor'
                    print('You have been assigned to be an advisor for this group.')
                    print(f'Logging out. The program has to log out because the role changed.')
                    sys.exit()
                elif i['Advisor'] != '-':
                    print('This group already has an advisor.')
                    advisor_pending.update('ProjectID', project_id, 'to_be_advisor', self.id, 'Response', 'Denied')
                    advisor_pending.update('ProjectID', project_id, 'to_be_advisor', self.id, 'Response_date', datetime.now())
                    save('advisor_pending_request')

        elif choice.lower() == 'deny':
            advisor_pending.update('ProjectID', project_id, 'to_be_advisor', self.id, 'Response', 'Denied')
            advisor_pending.update('ProjectID', project_id, 'to_be_advisor', self.id, 'Response_date', datetime.now())
            save('advisor_pending_request')
            print(f'You have denied to be an advisor for this group ({project_id}).')

    def see_all_projects_details(self):
        print(project_table)

    def eval_project(self):
        print('Project available for evaluation: ')
        print(project_table.filter(lambda x: x['Status'] == 'sent').filter(lambda x: x["Evaluator"] == '-'))
        if project_table.filter(lambda x: x['Status'] == 'sent').filter(lambda x: x["Evaluator"] == '-').table:
            choose_project = input('Choose the project to respond (ProjectID): ')
            project_table.update2('ProjectID', choose_project, 'Evaluator', self.id)
            save('project')
            result = input('Result (pass/reject): ')
            if result.lower() == 'pass':
                feedback = input(f'Feedback of the evaluation: ')
                project_table.update2("ProjectID", choose_project, "Result", 'passed')
                project_table.update2("ProjectID", choose_project, "Feedback", feedback)
                save('project')
            elif result.lower() == "reject":
                feedback = input(f'Feedback of the evaluation: ')
                project_table.update2("ProjectID", choose_project, "Result", 'rejected')
                project_table.update2("ProjectID", choose_project, "Feedback", feedback)
                save('project')
        elif not project_table.filter(lambda x: x['Status'] == 'sent').filter(lambda x: x["Evaluator"] == '-').table:
            print('There is no project to evaluate.')


class Advisor:
    def __init__(self, uid, username, role, project_id):
        self.id = uid
        self.user = username
        self.role = role
        self.project_id = project_id

    def update_status(self):
        status = input('Update the project status: ')
        project_table.update2('ProjectID', self.project_id, 'Status', status)
        print('Project Status Updated.')
        save('project')

    def see_project_detail(self):
        print(project_table.filter(lambda x: x['Advisor'] == self.id))

    def approval(self):
        eval_result = project_table.filter(lambda x: x['ProjectID'] == self.project_id).select('Result')
        if eval_result[0]['Result'] == 'passed':
            choice = input('Enter your approval (Approve/Disapprove): ')
            if choice.lower() == 'approve':
                project_table.update2('ProjectID', self.project_id, 'Approval', 'approved')
                save('project')
                print(f'You approved the project ({self.project_id}).')
            elif choice.lower() == 'disapprove':
                project_table.update2('ProjectID', self.project_id, 'Approval', 'disapproved')
                save('project')
                print(f'You disapproved the project ({self.project_id}).')

        else:
            print("The project hasn't passed the evaluation yet.")

    def eval_project(self):
        print('Project available for evaluation: ')
        print(project_table.filter(lambda x: x['Status'] == 'sent').filter(lambda x: x["Evaluator"] == '-'))
        if project_table.filter(lambda x: x['Status'] == 'sent').filter(lambda x: x["Evaluator"] == '-').table:
            choose_project = input('Choose the project to respond (ProjectID): ')
            project_table.update2('ProjectID', choose_project, 'Evaluator', self.id)
            save('project')
            result = input('Result (pass/reject): ')
            if result.lower() == 'pass':
                feedback = input(f'Feedback of the evaluation: ')
                project_table.update2("ProjectID", choose_project, "Result", 'passed')
                project_table.update2("ProjectID", choose_project, "Feedback", feedback)
                save('project')
            elif result.lower() == "reject":
                feedback = input(f'Feedback of the evaluation: ')
                project_table.update2("ProjectID", choose_project, "Result", 'rejected')
                project_table.update2("ProjectID", choose_project, "Feedback", feedback)
                save('project')
        elif not project_table.filter(lambda x: x['Status'] == 'sent').filter(lambda x: x["Evaluator"] == '-').table:
            print('There is no project to evaluate.')


class Admin:
    def __init__(self, uid, username, role):
        self.id = uid
        self.user = username
        self.role = role

    def see_all_projects_details(self):
        print(project_table)

    def student_no_project(self):
        print(login_table.filter(lambda x: x['role'] == 'student'))

    def faculty_no_project(self):
        print(login_table.filter(lambda x: x['role'] == 'faculty'))

    def edit_database(self):
        while True:
            print()
            choice = input('Choose an option: \n'
                           '1. Add Information\n'
                           '2. Delete Information\n'
                           '0. Go back to previous page\n'
                           'Choose a number 1,2 and 0: ')
            if choice == '1':
                first = input('Input first name: ')
                last = input('Input last name: ')
                user_id = input('Input ID: ')
                role = input('student or faculty: ')
                username = first + '.' + last[0]
                password = random.randint(1000, 9999)
                person_table.table.append({'ID': user_id, 'first': first, 'last': last, 'type': role})
                login_table.table.append({'ID': user_id, 'username': username, 'password': password, 'role': role})
                print(f'{first} {last} ({user_id}) successfully added to the database.')
            elif choice == '2':
                id_remove = input('Input ID of the person you want to delete : ')
                for i in range(len(person_table.table)):
                    if person_table.table[i]['ID'] == id_remove:
                        person_table.table.pop(i)
                for i in range(len(login_table.table)):
                    if login_table.table[i]['ID'] == id_remove:
                        login_table.table.pop(i)
                for i in range(len(project_table.table)):
                    if project_table.table[i]['Member1'] == id_remove:
                        project_table.table[i]['Member1'] = None
                    elif project_table.table[i]['Member2'] == id_remove:
                        project_table.table[i]['Member2'] = None
                print(f'Successfully deleted {id_remove} from the database.')
            elif choice == '0':
                break

            else:
                print('Invalid choice. Please choose the valid choices (1,2 and 0)')
        save('persons')
        save('login')
        save('project')


def initializing():
    db = DB()
    persons_csv = CSVReader('persons.csv').read_csv()
    persons_table = Table('persons', persons_csv)
    db.insert(persons_table)

    login_csv = CSVReader('login.csv').read_csv()
    login_table = Table('login', login_csv)
    db.insert(login_table)

    project_csv = CSVReader('project.csv').read_csv()
    project_table = Table('project', project_csv)
    db.insert(project_table)

    advisor_pending_csv = CSVReader('advisor_pending_request.csv').read_csv()
    advisor_pending_request_table = Table('advisor_pending_request', advisor_pending_csv)
    db.insert(advisor_pending_request_table)

    member_pending_csv = CSVReader('member_pending_request.csv').read_csv()
    member_pending_request_table = Table('member_pending_request', member_pending_csv)
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
    else:
        print('The login table is not found.')
        return None


def save(table_name):
    search_table = main_db.search(table_name)
    my_file = open(table_name + ".csv", "w")
    writer = csv.writer(my_file)
    x = search_table.table[0].keys()
    writer.writerow(x)
    for dict in search_table.table:
        writer.writerow(dict.values())
    with open(table_name + ".csv", "r") as myFile:
        print(myFile.read())


main_db = initializing()
val = login()
login_table = main_db.search('login')
person_table = main_db.search('persons')
member_pending = main_db.search('member_pending_request')
advisor_pending = main_db.search('advisor_pending_request')
project_table = main_db.search('project')
user_id = login_table.filter(lambda x: x['username'] == val[0]).select('ID')


if val[1] == 'admin':
    admin_user = Admin(user_id[0]['ID'], val[0], val[1])
    while True:
        print()
        print(f'User: {val[0]} (ID: {user_id[0]["ID"]})')
        print(f'Choose function for admin: ')
        print('1. See all project information')
        print("2. See all student that didn't join any project")
        print("3. See all faculty that didn't advise any project")
        print('4. Edit database')
        print('0. Exit the program')
        choice = int(input("Enter your choice: "))
        print()
        if choice == 1:
            admin_user.see_all_projects_details()
        elif choice == 2:
            admin_user.student_no_project()
        elif choice == 3:
            admin_user.faculty_no_project()
        elif choice == 4:
            admin_user.edit_database()
        elif choice == 0:
            print('Exiting the program.')
            sys.exit()
        else:
            print('Invalid choice. Please choose the valid choices (1,2,3,4 and 0)')

elif val[1] == 'student':
    student_user = Student(user_id[0]['ID'], val[0], val[1])
    while True:
        print()
        print(f'User: {val[0]} (ID: {user_id[0]["ID"]})')
        print(f'Choose function for student: ')
        print('1. See your invitations')
        print('2. Respond to the invitations')
        print("3. Create a project")
        print('0. Exit the program')
        choice = int(input("Enter your choice: "))
        print()
        if choice == 1:
            if member_pending:
                student_user.see_invitation_req()
            else:
                print('Invalid choice. Please choose the valid choices (1,2,3 and 0)')
        elif choice == 2:
            project_id = input('Which project do you want to respond? (Project ID): ')
            response = input('What is your response? (accept/deny): ')
            if member_pending:
                for req in range(len(member_pending.filter(lambda x: x['ProjectID'] == project_id).table)):
                    if member_pending.filter(lambda x: x['ProjectID'] == project_id).table[req]['to_be_member'] == user_id[0]['ID']:
                        if response.lower() == 'accept':
                            student_user.respond_invitation('accept', project_id)
                        elif response.lower() == 'deny':
                            student_user.respond_invitation('deny', project_id)
                        else:
                            print('Invalid choice. Please try again.')
            else:
                print('Member pending request table is not found.')
        elif choice == 3:
            student_user.create_project()
        elif choice == 0:
            print('Exiting the program.')
            sys.exit()
        else:
            print('Invalid choice. Please choose the valid choices (1,2,3 and 0)')


elif val[1] == 'advisor':
    advisor_projectid = project_table.filter(lambda x: x['Advisor'] == user_id[0]['ID']).select('ProjectID')
    advisor_user = Advisor(user_id[0]['ID'], val[0], val[1], advisor_projectid[0]['ProjectID'])
    while True:
        print()
        print(f'User: {val[0]} (ID: {user_id[0]["ID"]})')
        print(f'Choose function for advisor: ')
        print('1. Update project status')
        print('2. See project detail')
        print('3. Send project approval')
        print('4. Evaluate project')
        print('0. Exit the program')
        choice = int(input("Enter your choice: "))
        print()
        if choice == 1:
            advisor_user.update_status()
        elif choice == 2:
            advisor_user.see_project_detail()
        elif choice == 3:
            advisor_user.approval()
        elif choice == 4:
            advisor_user.eval_project()
        elif choice == 0:
            print('Exiting the program.')
            sys.exit()
        else:
            print('Invalid choice. Please choose the valid choices (1,2,3,4 and 0)')

elif val[1] == 'lead':
    lead_projectid = project_table.filter(lambda x: x['Lead'] == user_id[0]['ID']).select('ProjectID')
    lead_user = Lead(user_id[0]['ID'], val[0], val[1], lead_projectid[0]['ProjectID'])
    while True:
        print()
        print(f'User: {val[0]} (ID: {user_id[0]["ID"]})')
        print(f'Choose function for lead: ')
        print('1. See project detail')
        print('2. Send an invitation to a student')
        print('3. Send an invitation to an advisor')
        print('4. Send project')
        print('5. View evaluation results')
        print('0. Exit the program')
        choice = int(input("Enter your choice: "))
        print()
        if choice == 1:
            lead_user.see_detail()
        elif choice == 2:
            lead_user.send_invite_to_student()
        elif choice == 3:
            lead_user.send_req_to_advisor()
        elif choice == 4:
            lead_user.send_project()
        elif choice == 5:
            lead_user.see_eval_result()
        elif choice == 0:
            print('Exiting the program.')
            sys.exit()
        else:
            print('Invalid choice. Please choose the valid choices (1,2,3,4,5 and 0)')

elif val[1] == 'member':
    member_projectid = project_table.filter(lambda x: x['Member1'] or x['Member2'] == user_id[0]['ID']).select('ProjectID')
    member_user = Member(user_id[0]['ID'], val[0], val[1], member_projectid[0]['ProjectID'])
    while True:
        print()
        print(f'User: {val[0]} (ID: {user_id[0]["ID"]})')
        print(f'Choose function for member: ')
        print('1. See project detail')
        print('2. See invitations sent to student')
        print('0. Exit the program')
        choice = int(input("Enter your choice: "))
        print()
        if choice == 1:
            member_user.see_project_detail()
        elif choice == 2:
            member_user.see_group_pending_invites()
        elif choice == 0:
            print('Exiting the program.')
            sys.exit()
        else:
            print('Invalid choice. Please choose the valid choices (1,2 and 0)')

elif val[1] == 'faculty':
    faculty_user = Faculty(user_id[0]['ID'], val[0], val[1])
    while True:
        print()
        print(f'User: {val[0]} (ID: {user_id[0]["ID"]})')
        print(f'Choose function for faculty: ')
        print('1. See your invitations')
        print('2. Respond to the invitations')
        print('3. See all projects details')
        print('4. Evaluate project')
        print('0. Exit the program')
        choice = int(input("Enter your choice: "))
        print()
        if choice == 1:
            faculty_user.advisor_pending_req()
        elif choice == 2:
            project_id = input('Which project do you want to respond? (Project ID): ')
            response = input('What is your response? (accept/deny): ')
            if member_pending:
                for req in range(len(advisor_pending.filter(lambda x: x['ProjectID'] == project_id).table)):
                    if advisor_pending.filter(lambda x: x['ProjectID'] == project_id).table[req]['to_be_advisor'] == user_id[0]['ID']:
                        if response.lower() == 'accept':
                            faculty_user.advisor_respond_req('accept', project_id)
                        elif response.lower() == 'deny':
                            faculty_user.advisor_respond_req('deny', project_id)
                        else:
                            print('Invalid choice. Please try again.')
            else:
                print('Member pending request table is not found.')
        elif choice == 3:
            faculty_user.see_all_projects_details()
        elif choice == 4:
            faculty_user.eval_project()
        elif choice == 0:
            print('Exiting the program.')
            sys.exit()
        else:
            print('Invalid choice. Please choose the valid choices (1,2,3,4 and 0)')

# exit()



