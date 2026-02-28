# File Triage Skill

## Purpose
This skill enables the AI employee to process incoming markdown files from the Inbox, analyze their content, determine appropriate action, and route them to the correct output folder.

## Prerequisites
- Access to vault/Inbox/ folder
- Access to vault/Needs_Action/ folder
- Access to vault/Done/ folder

## Step-by-Step Process

### 1. Reading the Task from Inbox
- Monitor the vault/Inbox/ folder for new .md files
- When a new file appears, read its entire content
- Parse the markdown structure to identify:
  - Title (typically the first # heading)
  - Description or body content
  - Any specific instructions or requirements
  - Deadline or urgency indicators
  - Contact information if present

### 2. Summarizing the Content
- Extract the main request or topic in 1-2 sentences
- Identify the key action items requested
- List any specific requirements mentioned
- Note the expected deliverable or outcome
- Record any constraints or special conditions

### 3. Decision Matrix: Needs Action vs Done
Use the following criteria to determine the file's destination:

#### Route to Needs_Action if:
- The file contains a task requiring execution
- The request needs research or data gathering
- The file asks for creation of new content or code
- The request requires analysis or processing
- The task involves contacting another system or person
- The file contains a problem that needs solving
- The request has multiple steps to complete

#### Route to Done if:
- The file is a completion notification
- The task has already been finished
- The file contains only informational content
- The request was exploratory with no required follow-up
- The task is marked as completed by sender
- The file is a status update without further action needed

### 4. Writing Output Markdown File
When creating the output file, follow this structure:

#### For Needs_Action files:
```
# Triage Summary: [Original Title]

## Original Request
[Copy the original request content]

## Summary
[1-2 sentence summary of the main request]

## Action Items
- [List specific tasks to be completed]

## Priority
[High/Medium/Low based on urgency]

## Notes
[Any additional context or constraints]
```

#### For Done files:
```
# Completed: [Original Title]

## Original Request
[Copy the original request content]

## Completion Status
[How the request was fulfilled]

## Action Taken
[Brief description of what was done]

## Outcome
[Result of the completed task]
```

### 5. File Naming Convention
- For Needs_Action: Use `triaged_[original_filename]`
- For Done: Use `completed_[original_filename]`
- Preserve the original timestamp if present

## Quality Checks
- Verify the original content was accurately copied
- Ensure the decision for routing was appropriate
- Check that the summary captures the essence of the request
- Confirm the output file is properly formatted
- Validate the file was moved to the correct destination folder

## Special Cases
- If the request is unclear, route to Needs_Action with a note asking for clarification
- If the request is outside of your abilities, route to Needs_Action with an explanation
- If a request conflicts with company policies, route to Needs_Action with a warning
- When in doubt, route to Needs_Action for human review

## Escalation
Route to Needs_Action with a note if:
- Request involves sensitive data
- Task requires human approval
- Deadline is unrealistic
- Requirements are vague or contradictory