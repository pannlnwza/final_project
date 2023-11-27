# Proposal

### Project Evaluation
This proposal outlines the steps for evaluating senior projects. 

**1. Notify the evaluators:**
The system sends a message to the evaluators that is not assigned, telling them about the project they can review. The project waiting for response will be added to the waiting list.

**2. Assign evaluator:**
The evaluator can choose the project to evaluate from the waiting list.

**3. Give access to evaluators:**
Give access to the evaluators to see project details that the evaluator chose to evaluate.

**4. Scoring:**
The evaluators will give score to specify criteria such as creativity, completeness.

**5. Notify the students:**
The system sends a message to the students, telling them about result and feedback of the evaluation.

**6. Final Approval:** 
Approval is granted if the project meets specified criteria and gets approve from the advisor.



### Code outline
**1. Notify the evaluators**
```py
evaluators = get_available_evaluators() 
for evaluator in evaluators:
    send_notification(evaluator, project)
```

**2. Assign evaluator**
```py
project.assign_evaluator(evaluator)
project.remove_from_waiting_list()
```

**3. Give access to evaluator**
```py
if project.has_evaluator(evaluator):
    evaluator.access_project_details(project)
```

**4. Scoring**
```py
project.evaluation_scores(evaluator, scores)
```

**5. Notify the students**
```py
project.get_member().notify(message)
```

**6. Final Approval**

Advisor Approval:
```py
project.get_advisor_approval(advisor)
```

Final Approval:
```py
if project.meets_criteria_for_approval() and advisor_approves(project, advisor):
    project.approve()
```