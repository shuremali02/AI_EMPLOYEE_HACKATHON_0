#!/usr/bin/env python3
"""
Create a business task for the AI Employee to process
"""
import os
from datetime import datetime

# Business post content
content = """🚀 Transform Your Business with AI Automation

In today's fast-paced market, businesses that leverage AI automation are seeing 85-90% cost reductions compared to traditional human resources while maintaining consistent, predictable performance.

Key business transformations:
• 24/7 automated operations without breaks
• Significant cost savings with AI employees
• Consistent quality and performance
• Scalable solutions that grow with your business

The future of business is autonomous. Companies that embrace AI-powered automation today will dominate their markets tomorrow. Don't get left behind - start your automation journey now!

Ready to revolutionize your business operations?

#BusinessAutomation #ArtificialIntelligence #DigitalTransformation #BusinessGrowth #Innovation #FutureOfWork #AI #Entrepreneurship"""

def create_task():
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the task file
    task_content = f"""# Business LinkedIn Post Task

## Objective
Create and post the following business content to LinkedIn using the MCP server:

{content}

## Instructions
- Use LinkedIn MCP server to authenticate and post
- Use Chromium browser automation
- Log into LinkedIn account
- Create new post with the above content
- Click post button to publish
- Log the activity in the vault system

## Priority
High

## Expected Workflow
1. MCP server receives request
2. Opens Chromium browser
3. Logs into LinkedIn account
4. Creates new post
5. Publishes content
6. Logs activity in vault
"""

    # Ensure the Inbox directory exists
    inbox_path = "AI_Employee_Vault/Inbox"
    os.makedirs(inbox_path, exist_ok=True)

    # Write the task file
    task_filename = f"business_linkedin_task_{timestamp}.md"
    task_path = os.path.join(inbox_path, task_filename)

    with open(task_path, 'w') as f:
        f.write(task_content)

    print(f"Created business task: {task_path}")
    print("The AI Employee will process this task using MCP servers and browser automation.")

if __name__ == "__main__":
    create_task()