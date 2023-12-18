# Project Management
## Files and Descriptions
These are all the **important** files that are needed to run the program. **If one of these files are missing the program will not run properly.**

1. **database.py**
      - **CSVReader**: Class for reading CSV files
        - `read_csv`: Read data from the CSV file and convert it into a list of dict.

      - **DB**: Class that contain database
        - `insert`: Insert a table into the database.
        - `search`: Search for a table in the database based on its name.
        
      - **Table**: Represents a table
        - `join`: Joins two tables based on a common key.
        - `filter`: Filters the table based on a given condition.
        - `select`: Selects specific attributes from the table.
        - `insert_table`: Inserts a new entry into the table.
        - `update`: Updates a specific key's value based on multiple conditions.
        - `update2`: Updates a specific key's value based on a single condition.


2. **project_manage.py**
   - Defines functions for initializing and then saving to the main database.
   - Classes for role-based activities
     - `Admin`: Represents an admin in the system.  
     - `Faculty`: Represents a faculty member in the system.
     - `Advisor`: Represents an advisor in the system.
     - `Lead`: Represents a lead in the system.
     - `Member`: Represents a member in the system.
     - `Student`: Represents a student in the system.


3. **CSV files**
   - persons.csv: This CSV file contains information about user's ID, firstname, lastname and type(role).
   - login.csv: This CSV file contains information of user's ID, username and password that is needed to use to log in.
   - project.csv: This CSV file will store the data of all the projects that are created.
   - member_pending_request.csv: This CSV file will store the data of member invitations.
   - advisor_pending_request.csv: This CSV file will store the data of advisor invitations.



## Execution

1. Clone the repository:

    ```bash
    git clone https://github.com/pannlnwza/final_project.git
    ```

2. Run the main program: (project_manage.py)

    ```bash
    python project_manage.py
    ```

## Interactions
- Every `student` can create a project group, after creating the role will change to `lead`.
- `Lead` can invite other `student` to be the member of the group. A `lead` can invite max of 2 members (not including lead).
- `Lead` can invite a `faculty` member to be an `advisor` of the project.
- `Faculty` members and `student` can respond to his/her invitations (accept or deny).
- If they accept the invitation a `faculty` will change the role to an `advisor`, and `student` will change the role to a `member`.

    **Note: After the role changed the program will automatically log you out. You have to re-login.**
- In the `lead` menu, there is a function to send the project for evaluation.
- After the `lead` sent the project. In the `advisor` or `faculty` menu there's a function called "evaluate project", if there's a project sent it will pop up in the "evaluate project". An `advisor` or `faculty` can choose a project to evaluate by inputting the projectID and give results(passed or rejected) and can give feedbacks too.
- After evaluation, the `lead` can view the evaluation result. If the project got rejected the `lead` can resend the project for evaluation again.
- If the evaluation result is passed, the `advisor` of the project can send an approval (approve or disapprove) of the project.

- ### Admin commands
  - **Edit database**
    - **Add Information**: An `admin` can add new user information by inputting firstname, lastname and role. The program will automatically generate a username, a random 7 letters ID and a password for the new user.
    - **Delete Information**: An `admin` can delete user's information by inputting the user ID.
    
    **Note: If you just added a new user information, you cannot delete it right after. You have to rerun the program to do so.**



## Roles and Actions

| Role    | Action                                               | Method                      | Class   | Completion (%) |
|---------|------------------------------------------------------|-----------------------------|---------|----------------|
| Admin   | See all project information                          | see_all_projects_details()  | Admin   | 100            |
| Admin   | See students without projects                        | student_no_project()        | Admin   | 100            |
| Admin   | See a faculty member who didn't advise any project   | faculty_no_project()        | Admin   | 100            |
| Admin   | Edit database                                        | edit_database()             | Admin   | 100            |
| Faculty | See pending invitations                              | advisor_pending_req()       | Faculty | 100            |
| Faculty | Respond to invitations                               | advisor_respond_req         | Faculty | 100            |
| Faculty | See all project details                              | see_all_projects_details()  | Faculty | 100            |
| Faculty | Evaluate project                                     | eval_project()              | Faculty | 100            |
| Advisor | Update project status                                | update_status()             | Advisor | 100            |
| Advisor | See project detail (The project that is advising)    | see_project_detail()        | Advisor | 100            |
| Advisor | Send project approval                                | approval()                  | Advisor | 100            |
| Advisor | Evaluate project                                     | eval_project()              | Advisor | 100            |
| Lead    | See project details                                  | see_detail()                | Lead    | 100            |
| Lead    | Send invitation to a student                         | send_invite_to_student()    | Lead    | 100            |
| Lead    | Send invitation to a faculty member to be an advisor | send_req_to_advisor()       | Lead    | 100            |
| Lead    | See invitations sent to student and faculty member   | see_group_pending_invites() | Lead    | 100            |
| Lead    | Send project for evaluation                          | send_project()              | Lead    | 100            |
| Lead    | View evaluation results                              | see_eval_result()           | Lead    | 100            |
| Member  | See project details                                  | see_project_detail()        | Member  | 100            |
| Member  | See invitations sent to student and faculty member   | see_group_pending_invites() | Member  | 100            |
| Student | See invitations                                      | see_invitation_req()        | Student | 100            |\
| Student | Respond to invitations                               | respond_invitation()        | Student | 100            |
| Student | Create a project                                     | create_project()            | Student | 100            |






## Missing Features
   - None. All the features that is planned to do is already done.

## Outstanding Bugs
   - When you use the edit database function when you're an admin you cannot add a new database and delete it immediately you have to rerun the program to delete the new database.
