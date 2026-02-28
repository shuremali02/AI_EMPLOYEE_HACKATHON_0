import argparse
import os
import time
import sys
from datetime import datetime

def request_approval(action, id):
    # Define base vault path
    base_path = "AI_Employee_Vault"
    approval_dir = os.path.join(base_path, "Needs_Approval")

    # Create approval directory if it doesn't exist
    os.makedirs(approval_dir, exist_ok=True)

    # Create approval request file
    filename = f"approval_{id}.md"
    filepath = os.path.join(approval_dir, filename)

    try:
        with open(filepath, 'w') as f:
            f.write(f"""---
type: approval_request
status: pending
action: {action.lower().replace(' ', '_')}
priority: medium
---

# Approval Request: {action}

## Action Required
{action}

## Status
- [ ] Pending approval

## Instructions
To approve: Change status from `pending` to `approved` in the frontmatter above

To reject: Change status from `pending` to `rejected` in the frontmatter above

## Created
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

        print(f"Approval request created: {filename}")

        # Wait for response with timeout
        timeout = 3600  # 1 hour timeout
        start_time = time.time()

        while time.time() - start_time < timeout:
            with open(filepath, 'r') as f:
                content = f.read()

            # For .md files, check frontmatter for status
            if 'status: approved' in content.lower():
                print(f"APPROVED: {action}")
                return
            elif 'status: rejected' in content.lower():
                print(f"REJECTED: {action}")
                return
            # For backward compatibility, also check for APPROVED/REJECTED in content
            elif 'APPROVED' in content.upper():
                print(f"APPROVED: {action}")
                return
            elif 'REJECTED' in content.upper():
                print(f"REJECTED: {action}")
                return

            time.sleep(5)  # Check every 5 seconds

        print(f"Failed to process approval: Timeout waiting for response for action '{action}'")
        sys.exit(1)

    except Exception as e:
        print(f"Failed to process approval: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Request human approval for sensitive actions")
    parser.add_argument("--action", required=True, help="Description of the action requiring approval")
    parser.add_argument("--id", required=True, help="Unique identifier for the approval request")

    args = parser.parse_args()

    request_approval(args.action, args.id)