#!/usr/bin/env python3
"""
AI Employee Scheduler
Automatically processes tasks from the Inbox and handles automated LinkedIn posting
"""

import os
import time
import subprocess
import sys
from datetime import datetime, timedelta
import glob
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_inbox_tasks():
    """
    Process any new tasks in the Inbox folder using the task-planner skill
    """
    inbox_path = "AI_Employee_Vault/Inbox"
    needs_action_path = "AI_Employee_Vault/Needs_Action"

    # Ensure directories exist
    os.makedirs(inbox_path, exist_ok=True)
    os.makedirs(needs_action_path, exist_ok=True)

    # Get all .md files in the Inbox
    inbox_files = glob.glob(os.path.join(inbox_path, "*.md"))

    if not inbox_files:
        logger.info("No new tasks found in Inbox")
        return True

    logger.info(f"Found {len(inbox_files)} task(s) in Inbox")

    # Process each new task
    for task_file in inbox_files:
        try:
            logger.info(f"Processing task: {task_file}")

            # Process this specific file using the task planner logic
            with open(task_file, 'r') as f:
                content = f.read()

            # Create a plan for this specific task
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_filename = f"Plan_{timestamp}.md"
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

            logger.info(f"Plan created: {plan_path}")

        except Exception as e:
            logger.error(f"Error processing {task_file}: {str(e)}")
            return False

    return True

def should_post_linkedin():
    """
    Determine if it's time to post on LinkedIn based on schedule
    Posts approximately once per day at a random time between 9 AM and 3 PM
    """
    now = datetime.now()

    # Check if we've already posted today
    log_dir = "AI_Employee_Vault/Logs"
    os.makedirs(log_dir, exist_ok=True)

    today_log = os.path.join(log_dir, f"linkedin_post_{now.strftime('%Y-%m-%d')}.log")

    if os.path.exists(today_log):
        logger.info("Already posted on LinkedIn today")
        return False

    # For this implementation, we'll post once per day between 9 AM and 3 PM
    # In a real implementation, you could make this more sophisticated
    if 9 <= now.hour <= 15:  # Between 9 AM and 3 PM
        # Add some randomness to not post at exactly the same minute every day
        # For demo purposes, we'll return True occasionally
        import random
        return random.random() > 0.7  # Post about 30% of the time during business hours

    return False

def post_linkedin_update():
    """
    Post an update to LinkedIn using the automated poster
    """
    try:
        logger.info("Attempting to post LinkedIn update...")

        # Import the LinkedIn poster
        sys.path.append(os.path.dirname(__file__))  # Add current directory to path
        from automated_linkedin_poster import LinkedInPoster

        poster = LinkedInPoster()
        success = poster.run_posting_cycle()

        if success:
            # Create a log file to mark that we've posted today
            now = datetime.now()
            log_dir = "AI_Employee_Vault/Logs"
            today_log = os.path.join(log_dir, f"linkedin_post_{now.strftime('%Y-%m-%d')}.log")

            with open(today_log, 'w') as f:
                f.write(f"LinkedIn post made at {now}\n")

            logger.info("LinkedIn post completed successfully")
            return True
        else:
            logger.error("Failed to post LinkedIn update")
            return False

    except ImportError as e:
        logger.warning(f"LinkedIn poster module not available: {e}")
        return False
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}")
        return False

def run_scheduler(interval_minutes=5):
    """
    Run the AI Employee scheduler continuously with specified interval
    """
    logger.info(f"AI Employee Scheduler started (checking every {interval_minutes} minutes)")

    while True:
        try:
            # Process inbox tasks
            success = process_inbox_tasks()
            if success:
                logger.info("Task processing completed successfully")
            else:
                logger.warning("Task processing completed with errors")

            # Check if it's time for LinkedIn posting
            if should_post_linkedin():
                post_linkedin_update()

        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")

        logger.info(f"Waiting {interval_minutes} minutes until next check...")
        time.sleep(interval_minutes * 60)

def main():
    parser = argparse.ArgumentParser(description='AI Employee Task Scheduler')
    parser.add_argument('--interval', type=int, default=5,
                        help='Interval in minutes between checks (default: 5)')
    parser.add_argument('--run-once', action='store_true',
                        help='Run once then exit (default: run continuously)')

    args = parser.parse_args()

    logger.info("AI Employee Scheduler started")

    if args.run_once:
        # Run once and exit
        try:
            success = process_inbox_tasks()

            # Check if it's time for LinkedIn posting
            if should_post_linkedin():
                post_linkedin_update()

            if success:
                logger.info("Task processing completed successfully")
            else:
                logger.warning("Task processing completed with errors")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            sys.exit(1)
    else:
        # Run continuously
        run_scheduler(args.interval)

if __name__ == "__main__":
    main()