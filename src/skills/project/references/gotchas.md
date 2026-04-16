# Project Gotchas

- A successful project create does not guarantee every optional field persisted; verify dates and lead/member changes.
- Use workspace statuses, not hard-coded strings.
- If the user says "one year from today", convert it to an exact date before writing.
- Do not ask for priority at the project layer unless the backend actually supports it; redirect priority to tasks when appropriate.
- Do not stop after project creation if the user's real goal was to get the work ready to execute.
