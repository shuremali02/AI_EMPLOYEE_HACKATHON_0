#!/usr/bin/env python3
"""
Create a LinkedIn post task in the vault
"""
import os
from datetime import datetime

def create_linkedin_task():
    # Content for the LinkedIn post
    content = """🚀 AI Employee: Revolutionizing the Business Landscape

The integration of AI Employees is creating unprecedented changes in the business market, fundamentally transforming how we approach operations, productivity, and growth.

Key transformations:
• 24/7 automated business operations
• Cost reduction by 85-90% compared to human FTEs
• Consistent, predictable performance
• Scalable automation across all business functions

The future of business is autonomous, and companies that embrace AI Employees today will have a significant competitive advantage.

#AI #ArtificialIntelligence #BusinessTransformation #Automation #Innovation #FutureOfWork #DigitalTransformation"""

    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the task file
    task_content = f"""# LinkedIn Post Task

## Objective
Create and post the following content to LinkedIn:

{content}

## Instructions
- Use the LinkedIn MCP server to post this content
- If automatic posting fails, create an approval request for manual posting
- Track engagement after posting

## Priority
High
"""

    # Ensure the Inbox directory exists
    inbox_path = "AI_Employee_Vault/Inbox"
    os.makedirs(inbox_path, exist_ok=True)

    # Write the task file
    task_filename = f"linkedin_post_task_{timestamp}.md"
    task_path = os.path.join(inbox_path, task_filename)

    with open(task_path, 'w') as f:
        f.write(task_content)

    print(f"Created LinkedIn post task: {task_path}")
    print("The scheduler will process this task and attempt to post to LinkedIn.")
    print("Check AI_Employee_Vault/Needs_Action/ for any approval requests if automatic posting fails.")

if __name__ == "__main__":
    create_linkedin_task()