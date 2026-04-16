VERIFICATION_PROMPT = """\
## Pre-Completion Verification

You are about to finish. Before completing, verify your work:

1. Re-read the user's original request (the first human message in this conversation)
2. Check that every requirement has been addressed — don't skip any part of the ask
3. Review any files you created or modified — do they look correct?
4. Check your todo list — are all items marked as completed?
5. If you made api_request calls, verify the responses were successful (2xx status)

If everything checks out, respond with your final summary to the user.
If something is missing or wrong, fix it now before responding.
"""
