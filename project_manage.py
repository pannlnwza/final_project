import csv
import sys
import random
from datetime import datetime
from database import DB, Table, CSVReader


def initializing():
    """
    Initialize the database and tables with CSV data.
    """
    db = DB()

    # Read data from CSV file and create tables
    persons_csv = CSVReader('persons.csv').read_csv()
    table_persons = Table('persons', persons_csv)
    db.insert(table_persons)

    login_csv = CSVReader('login.csv').read_csv()
    table_login = Table('login', login_csv)
    db.insert(table_login)

    project_csv = CSVReader('project.csv').read_csv()
    table_project = Table('project', project_csv)
    db.insert(table_project)

    advisor_pending_csv = CSVReader('advisor_pending_request.csv').read_csv()
    advisor_pending_request_table = Table('advisor_pending_request', advisor_pending_csv)
    db.insert(advisor_pending_request_table)

    member_pending_csv = CSVReader('member_pending_request.csv').read_csv()
    member_pending_request_table = Table('member_pending_request', member_pending_csv)
    db.insert(member_pending_request_table)
    return db


def login():
    """
    Checks if the username and password is correct.
    """
    db = initializing()
    login_t = db.search('login')
    if login_t:
        while True:
            username = input('Enter your username: ')
            password = input('Enter your password: ')
            for person in login_t.table:
                if person['username'] == username and person['password'] == password:
                    print(f'Welcome to the Program, {username}')
                    return [person['username'], person['role']]
            print('Invalid username or password. Please try again.')
    else:
        print('The login table is not found.')
        return None


def save(table_name):
    """
    Save the tables data to a CSV file.
    """
    search_table = main_db.search(table_name)
    with open(table_name + ".csv", "w", newline='') as my_file:
        writer = csv.writer(my_file)
        head = search_table.table[0].keys()
        writer.writerow(head)
        for row in search_table.table:
            writer.writerow(row.values())


def exit():
    """
    Save all data to CSV file before exiting the program.
    """
    save('persons')
    save('project')
    save('member_pending_request')
    save('advisor_pending_request')
    sys.exit()


class Student:
    """
    Represents a student in the system.
    """
    def __init__(self, uid, username, role):
        self.id = uid
        self.user = username
        self.role = role

    def see_invitation_req(self):
        """
        Display pending invitations for the student.
        """
        n = 0   # A variable to check if there's any invitation
        print('Showing a list of your pending invitations: ')
        for inv in member_pending.table:
            if self.id == inv['to_be_member']:
                print(inv)
                n += 1  # Check if there is an invitation
        if n == 0:
            print("You don't have any invitations yet.")
        return n

    def respond_invitation(self, respond, project):
        """
        Respond to a group invitation (accept or deny).
        """
        if respond.lower() == 'accept':
            for i in project_table.filter(lambda x: x['ProjectID'] == project).table:
                if i['Member1'] == '-':  # Check if the group is full or not
                    project_table.update('ProjectID', project, 'Member1', '-', 'Member1', self.id)
                elif i['Member1'] != '-' and i['Member2'] == '-':
                    project_table.update('ProjectID', project, 'Member2', '-', 'Member2', self.id)
                else:
                    print('This group is already full.')
                    return

            member_pending.update('ProjectID', project, 'to_be_member', self.id, 'Response', 'Accepted')
            member_pending.update('ProjectID', project, 'to_be_member', self.id, 'Response_date', datetime.today())
            save('member_pending_request')

            other_group_invite = member_pending.filter(lambda x: x['ProjectID'] != project
                                                       and x['to_be_member'] == self.id)
            for i in range(len(other_group_invite.table)):  # Automatically deny other invitations
                other_project_id = other_group_invite.table[i].get('ProjectID')
                member_pending.update('ProjectID', other_project_id, 'to_be_member', self.id, 'Response', 'Denied')
                member_pending.update('ProjectID', other_project_id, 'to_be_member',
                                      self.id, 'Response_date', datetime.today())
                save('member_pending_request')

            login_table.update('ID', self.id, 'username', self.user, 'role', 'member')
            person_table.update2('ID', self.id, 'type', 'member')
            save('login')
            save('project')
            save('persons')
            self.role = 'member'
            print(f'You have successfully joined the group ({project})')
            print('Please Re-login. The program has to log out because the role changed.')
            sys.exit()
        elif respond.lower() == 'deny':
            member_pending.update('ProjectID', project, 'to_be_member', self.id, 'Response', 'Denied')
            member_pending.update('ProjectID', project, 'to_be_member', self.id, 'Response_date', datetime.today())
            save('member_pending_request')
            print('You have denied the invitation.')

    def create_project(self):
        """
        Create a new project.
        """
        print('Enter "BACK" if you want to go back to previous page!')
        project_title = input("Enter your project title: ")
        if project_title == 'BACK':
            return
        login_table.update('ID', self.id, 'username', self.user, 'role', 'lead')
        person_table.update2('ID', self.id, 'type', 'lead')
        save('login')
        save('persons')
        _project_id = ''
        self.role = 'lead'
        for i in range(6):  # Create a random number for ProjectID
            num = str(random.randint(0, 9))
            _project_id += num
        project = {'ProjectID': _project_id,
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
        print('Please Re-login. The program has to log out because the role changed.')
        sys.exit()


class Member:
    """
    Represents a member in the system.
    """
    def __init__(self, uid, username, role, project_id):
        if role not in ('member','lead','admin'):
            raise ValueError('You have to be a member to use these functions.')
        self.id = uid
        self.user = username
        self.role = role
        self.project_id = project_id

    def see_project_detail(self):
        """
        Display details of the member's project.
        """
        for i in range(len(project_table.filter(lambda x: x['ProjectID'] == self.project_id).table)):
            for key, value in project_table.filter(lambda x: x['ProjectID'] == self.project_id).table[i].items():
                print(f'{key}: {value}')

    def see_group_pending_invites(self):
        """
        Display pending invitations for the member's group.
        """
        member_invites = member_pending.filter(lambda x: x['ProjectID'] == self.project_id)
        advisor_invites = advisor_pending.filter(lambda x: x['ProjectID'] == self.project_id)
        if member_invites.table or advisor_invites.table:
            print('Showing a list of invitations that has been sent to a student:')
            for i in range(len(member_invites.table)):
                print(member_invites.table[i])
            print()
            print('Showing a list of invitations that has been sent to a faculty:')
            for i in range(len(advisor_invites.table)):
                print(advisor_invites.table[i])
        else:
            print('There is no invitation sent.')


class Lead:
    """
    Represents a lead in the system.
    """
    def __init__(self, uid, username, role, project_id):
        if role not in ('lead', 'admin'):
            raise ValueError('You need be be a project lead to use these functions.')
        self.id = uid
        self.user = username
        self.role = role
        self.project_id = project_id

    def see_detail(self):
        """
        Display details of the lead's project.
        """
        for i in range(len(project_table.filter(lambda x: x['ProjectID'] == self.project_id).table)):
            for key, value in project_table.filter(lambda x: x['ProjectID'] == self.project_id).table[i].items():
                print(f'{key}: {value}')

    def send_invite_to_student(self):
        """
        Send an invitation to a student to join the project group.
        """
        print('Enter "BACK" if you want to go back to previous page!')
        new_member_id = input('Who do you want to invite?(ID): ')
        if new_member_id == 'BACK':
            return
        # User's project
        myproject = project_table.filter(lambda x: x['ProjectID'] == self.project_id).table
        # Check if the invited user is a student
        check_student = login_table.filter(lambda x: x['ID'] == new_member_id).select('role')
        if (check_student[0]['role'] != 'student' and check_student[0]['role'] != 'member'
           and check_student[0]['role'] != 'lead'):
            print(f'This user (ID: {new_member_id}) is not a student. Please try again.')
            return  # Return if the invited user is not a student
        if new_member_id == self.id:
            print('You cannot invite yourself to the group.. But WHY??')
            return  # Return if you invited yourself
        other_group = project_table.filter(lambda x: new_member_id in (x['Member1'], x['Member2'], x['Lead'])).table
        if other_group:
            print(f'This student (ID: {new_member_id}) is already a member of another group.')
            return  # Return if the invited user is already in another group

        for i in range(len(member_pending.table)):
            for inv in member_pending.filter(lambda x: x['ProjectID'] == self.project_id).table:
                if myproject[0]['Member1'] != '-' and myproject[0]['Member2'] != '-':
                    print('Your group is already full.')
                    return  # Return if the group is already full
                if new_member_id in (myproject[0]['Member1'], myproject[0]['Member2']):
                    print(f'This user (ID: {new_member_id}) is already in your group.')
                    return  # Return if the invited user is already in the group
                if inv['to_be_member'] == new_member_id and inv['Response'] == '-':
                    print(f'You already sent an invitation to this user (ID: {new_member_id}).')
                    return  # Return if this user is already invited

        # Add a member pending invitation to the CSV file
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

    def send_req_to_advisor(self):
        """
        Send a request to a faculty to be and advisor of the project group.
        """
        print('Enter "BACK" if you want to go back to previous page!')
        new_advisor_id = input('Who do you want to invite?(ID): ')
        if new_advisor_id == 'BACK':
            return

        check_faculty = login_table.filter(lambda x: x['ID'] == new_advisor_id).select('role')
        if check_faculty[0]['role'] != 'faculty':
            print(f'This user (ID: {new_advisor_id}) is not a faculty member. Please try again.')
            return  # Return if the invited user is not a faculty member
        myproject = project_table.filter(lambda x: x['ProjectID'] == self.project_id).table
        other_group = project_table.filter(lambda x: x['Advisor'] == new_advisor_id).table
        if other_group:
            print(f'This faculty (ID: {new_advisor_id}) is already a member of another group.')
            return  # Return if the invited user is already in another group

        for i in range(len(advisor_pending.table)):
            for inv in advisor_pending.filter(lambda x: x['ProjectID'] == self.project_id).table:
                if myproject[0]['Advisor'] != '-':
                    print('Your group is already has an advisor.')
                    return  # Return if the group already has an advisor
                if new_advisor_id == myproject[0]['Advisor']:
                    print(f'This user (ID: {new_advisor_id}) is already an advisor for this group.')
                    return  # Return if the invited user is already an advisor for this group
                if inv['to_be_advisor'] == new_advisor_id and inv['Response'] == '-':
                    print(f'You already sent an invitation to this user (ID: {new_advisor_id}).')
                    return  # Return if there's already an invitation sent to this user

        # Add an advisor pending invitation to the CSV file
        for project in project_table.filter(lambda x: x['ProjectID'] == self.project_id).table:
            if project['Advisor'] == '-':
                invitation_dict = {'ProjectID': self.project_id,
                                   'to_be_advisor': new_advisor_id,
                                   'Response': 'Pending',
                                   'Response_date': '-'}
                advisor_pending.insert_table(invitation_dict)
                print(f'An invitation has been sent to user {new_advisor_id} (faculty).')
                save('advisor_pending_request')
                return

    def see_group_pending_invites(self):
        """
        Display pending invitations for the project group.
        """
        member_invites = member_pending.filter(lambda x: x['ProjectID'] == self.project_id)
        advisor_invites = advisor_pending.filter(lambda x: x['ProjectID'] == self.project_id)
        if member_invites.table or advisor_invites.table:
            print('Showing a list of invitations that has been sent to a student.')
            for i in range(len(member_invites.table)):
                print(member_invites.table[i])
            print()
            print('Showing a list of invitations that has been sent to a faculty.')
            for i in range(len(advisor_invites.table)):
                print(advisor_invites.table[i])
        else:
            print('There is no invitation sent.')

    def send_project(self):
        """
        Send the project for evaluation.
        """
        print('Enter "BACK" if you want to go back to previous page!')
        choice = input('Do you want to send the project? (Y/N): ')
        if choice == 'BACK':
            return
        if choice.lower() == 'y':
            project_table.update2('ProjectID', self.project_id, 'Status', 'sent')
            project_table.update2('ProjectID', self.project_id, 'Approval', '-')
            save('project')
            print('You sent the project.')
        elif choice.lower() == 'n':
            pass

    def see_eval_result(self):
        """
        Display the evaluation results for the project.
        """
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
    """
    Represents a faculty member in the system.
    """
    def __init__(self, uid, username, role):
        if role not in ('faculty', 'advisor', 'admin'):
            raise ValueError('You have to be a faculty member to use these functions.')
        self.id = uid
        self.user = username
        self.role = role

    def advisor_pending_req(self):
        """
        Display pending advisor requests for the faculty member.
        """
        n = 0   # A variable to check if there's any invitation
        print('Showing a list of your pending invitations: ')
        for inv in advisor_pending.table:
            if self.id == inv['to_be_advisor']:
                print(inv)
                n += 1  # Check if there is an invitation
        if n == 0:
            print("You don't have any invitations yet.")
        return n

    def advisor_respond_req(self, respond, project):
        """
        Respond to advisor requests.
        """
        if respond.lower() == 'accept':
            for i in project_table.filter(lambda x: x['ProjectID'] == project).table:
                if i['Advisor'] == '-':
                    project_table.update('ProjectID', project, 'Advisor', '-', 'Advisor', self.id)
                    save('project')
                    advisor_pending.update('ProjectID', project, 'to_be_advisor', self.id, 'Response', 'Accepted')
                    advisor_pending.update('ProjectID', project, 'to_be_advisor',
                                           self.id, 'Response_date', datetime.today())
                    save('advisor_pending_request')

                    other_group_invite = member_pending.filter(lambda x: x['ProjectID'] != project
                                                               and x['to_be_advisor'] == self.id)
                    for index in range(len(other_group_invite.table)):  # Automatically deny other invitations
                        other_project_id = other_group_invite.table[i].get('ProjectID')
                        advisor_pending.update('ProjectID', other_project_id, 'to_be_advisor', self.id, 'Response',
                                               'Denied')
                        advisor_pending.update('ProjectID', other_project_id, 'to_be_advisor', self.id, 'Response_date',
                                               datetime.today())
                        save('advisor_pending_request')

                    login_table.update('ID', self.id, 'username', self.user, 'role', 'advisor')
                    person_table.update2('ID', self.id, 'type', 'advisor')
                    save('login')
                    save('persons')
                    self.role = 'advisor'
                    print('You have been assigned to be an advisor for this group.')
                    print('Please Re-login. The program has to log out because the role changed.')
                    sys.exit()
                elif i['Advisor'] != '-':   # Check if the group already has an advisor
                    print('This group already has an advisor.')
                    advisor_pending.update('ProjectID', project, 'to_be_advisor', self.id, 'Response', 'Denied')
                    advisor_pending.update('ProjectID', project, 'to_be_advisor',
                                           self.id, 'Response_date', datetime.today())
                    save('advisor_pending_request')

        elif respond.lower() == 'deny':
            advisor_pending.update('ProjectID', project, 'to_be_advisor', self.id, 'Response', 'Denied')
            advisor_pending.update('ProjectID', project, 'to_be_advisor', self.id, 'Response_date', datetime.today())
            save('advisor_pending_request')
            print(f'You have denied to be an advisor for this group ({project}).')

    def see_all_projects_details(self):
        """
        Display details of all projects.
        """
        print('Showing a list of all the project:')
        for i in range(len(project_table.table)):
            print(project_table.table[i])

    def eval_project(self):
        """
        Evaluate projects available for evaluation.
        """
        print('Project available for evaluation: ')
        # Display projects that are available for evaluation
        for i in range(len(project_table.filter(lambda x: x['Status'] == 'sent')
                           .filter(lambda x: x["Evaluator"] == '-').table)):
            print(project_table.filter(lambda x: x['Status'] == 'sent')
                  .filter(lambda x: x["Evaluator"] == '-').table[i])
        print()

        if project_table.filter(lambda x: x['Status'] == 'sent').filter(lambda x: x["Evaluator"] == '-').table:
            print('Enter "BACK" if you want to go back to previous page!')
            choose_project = input('Choose the project to respond (ProjectID): ')
            if choose_project == 'BACK':
                return

            # Update Evaluator of the project in the CSV file
            project_table.update2('ProjectID', choose_project, 'Evaluator', self.id)
            save('project')
            result = input('Result (pass/reject): ')
            if result.lower() == 'pass':
                feedback = input('Feedback of the evaluation: ')
                project_table.update2("ProjectID", choose_project, "Result", 'passed')
                project_table.update2("ProjectID", choose_project, "Feedback", feedback)
                save('project')
            elif result.lower() == "reject":
                feedback = input('Feedback of the evaluation: ')
                project_table.update2("ProjectID", choose_project, "Result", 'rejected')
                project_table.update2("ProjectID", choose_project, "Feedback", feedback)
                save('project')
        elif not project_table.filter(lambda x: x['Status'] == 'sent').filter(lambda x: x["Evaluator"] == '-').table:
            print('There is no project to evaluate.')


class Advisor:
    """
    Represents an advisor in the system.
    """
    def __init__(self, uid, username, role, project_id):
        if role not in ('advisor', 'admin'):
            raise ValueError('You have to be an advisor to use these functions.')
        self.id = uid
        self.user = username
        self.role = role
        self.project_id = project_id

    def update_status(self):
        """
        Update the project status.
        """
        print('Enter "BACK" if you want to go back to previous page!')
        status = input('Update the project status: ')
        if status == 'BACK':
            return
        project_table.update2('ProjectID', self.project_id, 'Status', status)
        print('Project Status Updated.')
        save('project')

    def see_project_detail(self):
        """
        Display details of the advisor's project.
        """
        for i in range(len(project_table.filter(lambda x: x['Advisor'] == self.id).table)):
            for key,value in project_table.filter(lambda x: x['Advisor'] == self.id).table[i].items():
                print(f'{key}: {value}')

    def approval(self):
        """
        Approve or disapprove the project based on evaluation results.
        """
        eval_result = project_table.filter(lambda x: x['ProjectID'] == self.project_id).select('Result')
        if eval_result[0]['Result'] == 'passed':
            print('Enter "BACK" if you want to go back to previous page!')
            approval = input('Enter your approval (Approve/Disapprove): ')
            if approval == 'BACK':
                return
            if approval.lower() == 'approve':
                project_table.update2('ProjectID', self.project_id, 'Approval', 'approved')
                save('project')
                print(f'You approved the project ({self.project_id}).')
            elif approval.lower() == 'disapprove':
                project_table.update2('ProjectID', self.project_id, 'Approval', 'disapproved')
                save('project')
                print(f'You disapproved the project ({self.project_id}).')
        else:
            print("The project hasn't passed the evaluation yet.")

    def eval_project(self):
        """
        Evaluate projects available for evaluation.
        """
        print('Project available for evaluation: ')
        # Display projects that are available for evaluation
        for i in range(len(project_table.filter(lambda x: x['Status'] == 'sent')
                           .filter(lambda x: x["Evaluator"] == '-').table)):
            print(project_table.filter(lambda x: x['Status'] == 'sent')
                  .filter(lambda x: x["Evaluator"] == '-').table[i])
        print()

        if project_table.filter(lambda x: x['Status'] == 'sent').filter(lambda x: x["Evaluator"] == '-').table:
            print('Enter "BACK" if you want to go back to previous page!')
            choose_project = input('Choose the project to respond (ProjectID): ')
            if choose_project == 'BACK':
                return
            project_table.update2('ProjectID', choose_project, 'Evaluator', self.id)
            save('project')
            result = input('Result (pass/reject): ')
            if result.lower() == 'pass':
                feedback = input('Feedback of the evaluation: ')
                project_table.update2("ProjectID", choose_project, "Result", 'passed')
                project_table.update2("ProjectID", choose_project, "Feedback", feedback)
                save('project')
            elif result.lower() == "reject":
                feedback = input('Feedback of the evaluation: ')
                project_table.update2("ProjectID", choose_project, "Result", 'rejected')
                project_table.update2("ProjectID", choose_project, "Feedback", feedback)
                save('project')
        elif not project_table.filter(lambda x: x['Status'] == 'sent').filter(lambda x: x["Evaluator"] == '-').table:
            print('There is no project to evaluate.')


class Admin:
    """
    Represents an admin in the system.
    """
    def __init__(self, uid, username, role):
        if role != 'admin':
            raise ValueError('You have to be an admin to use these functions.')
        self.id = uid
        self.user = username
        self.role = role

    def see_all_projects_details(self):
        """
        Display all the project's details.
        """
        print('Showing a list of all the project:')
        for i in range(len(project_table.table)):
            print(project_table.table[i])

    def student_no_project(self):
        """
        Display a list of student that isn't in a project group.
        """
        print('Showing a list of student who is not in a group: ')
        for i in range(len(login_table.filter(lambda x: x['role'] == 'student').table)):
            print(login_table.filter(lambda x: x['role'] == 'student').table[i])

    def faculty_no_project(self):
        """
        Display a list of faculty member that isn't an advisor.
        """
        print('Showing a list of faculty who is not an advisor: ')
        for i in range(len(login_table.filter(lambda x: x['role'] == 'faculty').table)):
            print(login_table.filter(lambda x: x['role'] == 'faculty').table[i])

    def edit_database(self):
        """
        Edit the database by adding or deleting information.
        """
        while True:
            choice = input('Choose an option: \n'
                           '1. Add Information\n'
                           '2. Delete Information\n'
                           '0. Go back to previous page\n'
                           'Choose a number 1,2 and 0: ')
            print()

            if choice == '1':
                first = input('Input first name: ')
                last = input('Input last name: ')
                role = input('Input type (student/faculty): ')
                uid = random.randint(1000000, 9999999)  # Random user id for the new user
                username = first + '.' + last[0]
                password = random.randint(1000, 9999)   # Random password for the new user
                person_table.table.append({'ID': uid, 'first': first, 'last': last, 'type': role})
                login_table.table.append({'ID': uid, 'username': username, 'password': password, 'role': role})
                save('persons')
                save('login')
                save('project')
                print(f'{first} {last} ({uid}) successfully added to the database.')
                print()
            elif choice == '2':
                id_remove = input('Input ID of the person you want to delete: ')
                for i in range(len(person_table.table)):
                    if person_table.table[i]['ID'] == id_remove:
                        person_table.table.pop(i)   # Remove user from the persons table
                for i in range(len(login_table.table)):
                    if login_table.table[i]['ID'] == id_remove:
                        login_table.table.pop(i)    # Remove user from the login table
                for i in range(len(project_table.table)):   # Remove user from the project table if user is a member
                    if project_table.table[i]['Member1'] == id_remove:
                        project_table.table[i]['Member1'] = None
                    elif project_table.table[i]['Member2'] == id_remove:
                        project_table.table[i]['Member2'] = None
                save('persons')
                save('login')
                save('project')
                print(f'Successfully deleted {id_remove} from the database.')
                print()
            elif choice == '0':
                save('persons')
                save('login')
                save('project')
                break
            else:
                print('Invalid choice. Please choose the valid choices (1,2 and 0)')


main_db = initializing()    # Main database
val = login()
login_table = main_db.search('login')   # Login table
person_table = main_db.search('persons')    # Persons table
member_pending = main_db.search('member_pending_request')   # Member pending table
advisor_pending = main_db.search('advisor_pending_request') # Advisor pending table
project_table = main_db.search('project')   # Project table
user_id = login_table.filter(lambda x: x['username'] == val[0]).select('ID')    # Search for the user's ID

if val[1] == 'admin':
    admin_user = Admin(user_id[0]['ID'], val[0], val[1])
    while True:
        print()
        print(f'User: {val[0]} (ID: {user_id[0]["ID"]})')
        print('Choose function for admin: ')
        print('1. See all project information')
        print("2. See all student that didn't join any project")
        print("3. See all faculty that didn't advise any project")
        print('4. Edit database')
        print('0. Exit the program')
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            admin_user.see_all_projects_details()
        elif choice == '2':
            admin_user.student_no_project()
        elif choice == '3':
            admin_user.faculty_no_project()
        elif choice == '4':
            admin_user.edit_database()
        elif choice == '0':
            print('Exiting the program.')
            sys.exit()
        else:
            print('Invalid choice. Please choose the valid choices (1,2,3,4 and 0)')

elif val[1] == 'student':
    student_user = Student(user_id[0]['ID'], val[0], val[1])
    while True:
        print()
        print(f'User: {val[0]} (ID: {user_id[0]["ID"]})')
        print('Choose function for student: ')
        print('1. See your invitations')
        print('2. Respond to the invitations')
        print("3. Create a project")
        print('0. Exit the program')
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            if member_pending:
                student_user.see_invitation_req()
            else:
                print('Invalid choice. Please choose the valid choices (1,2,3 and 0)')
        elif choice == '2':
            check = student_user.see_invitation_req()   # Check if there is an invitation
            if check == 0:
                continue
            print()
            print('Enter "BACK" if you want to go back to previous page!')
            project_id = input('Which project do you want to respond? (Project ID): ')
            if project_id.lower() == 'BACK':
                continue
            response = input('What is your response? (accept/deny): ')
            if response.lower() == 'back':
                continue
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
        elif choice == '3':
            student_user.create_project()
        elif choice == '0':
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
        print('Choose function for advisor: ')
        print('1. Update project status')
        print('2. See project detail')
        print('3. Send project approval')
        print('4. Evaluate project')
        print('0. Exit the program')
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            advisor_user.update_status()
        elif choice == '2':
            advisor_user.see_project_detail()
        elif choice == '3':
            advisor_user.approval()
        elif choice == '4':
            advisor_user.eval_project()
        elif choice == '0':
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
        print('Choose function for lead: ')
        print('1. See project detail')
        print('2. Send an invitation to a student')
        print('3. Send an invitation to an advisor')
        print('4. See invitations sent to student and faculty ')
        print('5. Send project')
        print('6. View evaluation results')
        print('0. Exit the program')
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            lead_user.see_detail()
        elif choice == '2':
            lead_user.send_invite_to_student()
        elif choice == '3':
            lead_user.send_req_to_advisor()
        elif choice == '4':
            lead_user.see_group_pending_invites()
        elif choice == '5':
            lead_user.send_project()
        elif choice == '6':
            lead_user.see_eval_result()
        elif choice == '0':
            print('Exiting the program.')
            sys.exit()
        else:
            print('Invalid choice. Please choose the valid choices (1,2,3,4,5 and 0)')

elif val[1] == 'member':
    member_projectid = project_table.filter(lambda x: x['Member1']
                                            or x['Member2'] == user_id[0]['ID']).select('ProjectID')
    member_user = Member(user_id[0]['ID'], val[0], val[1], member_projectid[0]['ProjectID'])
    while True:
        print()
        print(f'User: {val[0]} (ID: {user_id[0]["ID"]})')
        print('Choose function for member: ')
        print('1. See project detail')
        print('2. See invitations sent to student and faculty')
        print('0. Exit the program')
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            member_user.see_project_detail()
        elif choice == '2':
            member_user.see_group_pending_invites()
        elif choice == '0':
            print('Exiting the program.')
            sys.exit()
        else:
            print('Invalid choice. Please choose the valid choices (1,2 and 0)')

elif val[1] == 'faculty':
    faculty_user = Faculty(user_id[0]['ID'], val[0], val[1])
    while True:
        print()
        print(f'User: {val[0]} (ID: {user_id[0]["ID"]})')
        print('Choose function for faculty: ')
        print('1. See your invitations')
        print('2. Respond to the invitations')
        print('3. See all projects details')
        print('4. Evaluate project')
        print('0. Exit the program')
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            faculty_user.advisor_pending_req()
        elif choice == '2':
            check = faculty_user.advisor_pending_req()  # Check if there is an invitation
            if check == 0:
                continue
            print()
            print('Enter "BACK" if you want to go back to previous page!')
            project_id = input('Which project do you want to respond? (Project ID): ')
            if project_id == 'BACK':
                continue
            response = input('What is your response? (accept/deny): ')
            if response == 'BACK':
                continue
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
        elif choice == '3':
            faculty_user.see_all_projects_details()
        elif choice == '4':
            faculty_user.eval_project()
        elif choice == '0':
            print('Exiting the program.')
            sys.exit()
        else:
            print('Invalid choice. Please choose the valid choices (1,2,3,4 and 0)')

exit()
