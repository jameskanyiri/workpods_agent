# Project Workflows

## Project setup

1. Resolve workspace.
2. Read project statuses and members.
3. Capture project name, outcome, dates, and lead/member intent.
4. Update the project brief scratchpad.
5. Present a concise setup summary and confirm.
6. Create the project.
7. GET the project after creation and verify each field you set (`start_date`, `end_date`, `lead_user_id`, `member_ids`, `status_id`, etc.) actually appears populated in the response. The API silently drops unknown fields, so a 200 is not verification.
8. Recommend milestone-first structure if the project is still at a phase-level description.

## Project repair

1. Read the current project first.
2. Identify which fields are missing or wrong.
3. Ask only for the missing decision if one still exists.
4. Confirm if the change is material.
5. Patch the project.
6. Re-read to verify the repaired fields.

## Project summary

1. Read the project detail.
2. Distinguish what exists from what has not yet been created.
3. Summarize the current structure.
4. Recommend the single highest-value next move.
