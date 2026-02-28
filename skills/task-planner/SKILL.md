# Task Planner Skill

## Skill Name
Task Planner

## Description
This skill enables the AI employee to read incoming tasks from the vault/Inbox folder and create structured execution plans in the vault/Needs_Action folder. The skill ensures that all tasks are properly analyzed before execution with a clear plan of action.

## Purpose
- Transform unstructured task requests into detailed execution plans
- Ensure proper analysis and prioritization of tasks
- Maintain a record of planned work for tracking purposes
- Determine which tasks require human oversight

## Prerequisites
- Access to vault/Inbox/ folder
- Write permissions to vault/Needs_Action/ folder
- Ability to read and parse markdown files

## Workflow

### Step 1: Read Task
- Monitor vault/Inbox/ for new .md files
- Read the complete content of each new task file
- Parse the task content to identify:
  - Main objective
  - Requirements and constraints
  - Deadline or urgency
  - Expected deliverables

### Step 2: Analyze Intent
- Determine the primary goal of the task
- Identify the type of work required (research, writing, analysis, etc.)
- Assess complexity and scope
- Identify potential dependencies or requirements
- Recognize any special handling instructions

### Step 3: Break into Steps
- Decompose the task into discrete, actionable steps
- Organize steps in logical sequence
- Identify any parallelizable work
- Estimate time requirements for each step
- Note any required resources or information

### Step 4: Assign Priority
- Evaluate urgency based on deadlines or business impact
- Assess importance relative to other ongoing tasks
- Consider resource availability and dependencies
- Assign priority level:
  - **High**: Critical tasks with immediate deadlines or high impact
  - **Medium**: Important tasks with reasonable deadlines
  - **Low**: Non-urgent tasks or nice-to-have improvements

### Step 5: Check if Human Approval Needed
- Determine if the task involves sensitive information
- Assess if the task requires human judgment or decision-making
- Consider if the output will be used for critical business decisions
- Evaluate if the task involves external communication
- Flag tasks that exceed defined authority boundaries
- Response options: Yes/No

### Step 6: Save Plan.md to Needs_Action
- Create a new file in vault/Needs_Action/ with naming convention: `Plan_YYYYMMDD_HHMMSS.md`
- Include the following structured content:

```
# Task Plan

## Original Task
[Copy of the original task content]

## Objective
[Clear statement of what needs to be accomplished]

## Step-by-Step Plan
1. [First step with estimated time]
2. [Second step with estimated time]
3. [Third step with estimated time]
4. [Additional steps as needed]

## Priority
[High/Medium/Low with brief reasoning]

## Requires Human Approval?
[Yes/No with explanation]

## Suggested Output
[Description of the expected deliverable or outcome]
```

## Quality Assurance
- Verify that all original requirements are addressed in the plan
- Ensure steps are specific and actionable
- Confirm priority assignment is justified
- Check that human approval decision is properly documented
- Validate that the plan file is correctly formatted

## Special Considerations
- If a task is unclear or ambiguous, flag for human clarification in the plan
- For complex tasks, consider creating sub-plans for different phases
- If a task conflicts with existing work, note this in the plan
- For time-sensitive tasks, emphasize timeline requirements in the plan

## Escalation Criteria
Route to human supervisor if the task:
- Involves confidential or sensitive information
- Requires legal or compliance review
- Has unclear requirements that cannot be reasonably interpreted
- Represents a high-risk operation
- Falls outside the defined scope of AI employee capabilities

## Success Metrics
- Time from task receipt to plan creation: < 30 seconds
- Plan completeness: All required sections filled out
- Accuracy of priority assignments
- Correct identification of human approval requirements