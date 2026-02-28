#!/usr/bin/env python3
"""
AI Employee Scheduler
Automatically processes tasks from the Inbox using the task-planner skill
"""

import os
import time
import subprocess
import sys
from datetime import datetime
import glob

def process_inbox_tasks():
    """
    Process any new tasks in the Inbox folder using the task-planner skill
    """
    inbox_path = "AI_Employee_Vault/Inbox"

    # Get all .md files in the Inbox
    if not os.path.exists(inbox_path):
        print(f"{datetime.now()}: Inbox directory does not exist: {inbox_path}")
        os.makedirs(inbox_path, exist_ok=True)
        return True

    inbox_files = glob.glob(os.path.join(inbox_path, "*.md"))

    if not inbox_files:
        print(f"{datetime.now()}: No new tasks found in Inbox")
        return True

    print(f"{datetime.now()}: Found {len(inbox_files)} task(s) in Inbox")

    # Process each new task
    for task_file in inbox_files:
        try:
            print(f"{datetime.now()}: Processing task: {task_file}")

            # Process this specific file using the task planner logic
            with open(task_file, 'r') as f:
                content = f.read()

            # Create a plan for this specific task
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_filename = f"Plan_{timestamp}.md"
            needs_action_path = "AI_Employee_Vault/Needs_Action"
            plan_path = os.path.join(needs_action_path, plan_filename)

            # Create the detailed plan
            plan_content = f"""# Task Plan

## Original Task
{content}

## Objective
[Clear statement of what needs to be accomplished]

## Step-by-Step Plan
1. [First step]
2. [Second step]
3. [Third step]
4. [Additional steps as needed]

## Priority
[High/Medium/Low based on urgency and importance]

## Requires Human Approval?
[Yes/No - Consider complexity, impact, and policy requirements]

## Suggested Output
[Description of the expected deliverable or outcome]
"""

            # Write the plan file
            with open(plan_path, 'w') as plan_file:
                plan_file.write(plan_content)

            print(f"{datetime.now()}: Plan created: {plan_path}")

        except Exception as e:
            print(f"{datetime.now()}: Error processing {task_file}: {str(e)}")
            return False

    return True

def main():
    """
    Main function to run the AI Employee scheduler
    """
    print(f"{datetime.now()}: AI Employee Scheduler started")

    try:
        success = process_inbox_tasks()
        if success:
            print(f"{datetime.now()}: Task processing completed successfully")
        else:
            print(f"{datetime.now()}: Task processing completed with errors")
    except Exception as e:
        print(f"{datetime.now()}: Scheduler error: {str(e)}")

if __name__ == "__main__":
    main()