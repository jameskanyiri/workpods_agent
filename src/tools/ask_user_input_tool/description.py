ASK_USER_INPUT_TOOL_DESCRIPTION = """Ask the user structured questions with predefined answer options.

Use this instead of open-ended text questions when you need the user to choose between clear options,
select preferences, or rank priorities. This gives the user a faster, cleaner way to respond.

When to use:
- You need the user to pick a direction (e.g. which document to draft first)
- You need preferences or priorities (e.g. which sections matter most)
- You need a yes/no or A/B/C decision
- You want to confirm understanding before acting

When NOT to use:
- You need free-form input (names, descriptions, details) — just ask in a normal message instead
- The answer requires explanation or nuance that can't fit in 2-4 short options

Question types:
- single_select: User picks exactly one option. Use for decisions with one right answer.
- multi_select: User picks one or more. Use for "which of these apply" questions.
- rank_priorities: User drags to reorder. Use for "what matters most" questions.

Constraints:
- Max 3 questions per call.
- 2 to 4 options per question.
- Keep option labels short (2-5 words).
- Use plain, non-technical language. NEVER use file names, paths, or tool names in questions or options.

Args:
    questions: 1 to 3 question objects, each with question text, type, and options.
    display_name: A short label for the frontend. NEVER use file names or extensions. Examples: "Checking your preferences", "Confirming project direction", "Getting your input".
"""
