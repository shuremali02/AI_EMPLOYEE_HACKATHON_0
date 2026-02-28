# Vault File Manager Skill

Manage task workflow by moving files between vault directories.

## Usage
```python
python scripts/move_task.py --source "Inbox/filename.md" --destination "Needs_Action/filename.md"
```

## Inputs
- source: Source file path (Inbox/, Needs_Action/, or Done/)
- destination: Destination file path (Inbox/, Needs_Action/, or Done/)

## Output
- Success: "File moved successfully from [source] to [destination]"
- Error: "Failed to move file: [error message]"