THINK_TOOL_DESCRIPTION = """
    Pause and reflect — first person, confident, specific. 2–3 sentences. Max 40 words.
    State what you found, then what you're doing next and why. Reference content, not mechanics.

    The user can see this reflection, so write it as a natural status update they can follow along with.

    YES: "I've reviewed the project details — the budget section is missing personnel costs. I'm pulling the missing fields next."
    YES: "This is a detailed report that needs data from several sources. I'll start by reviewing what's available in the workspace."
    NO: "I will now use the think tool to analyze the request and then call ls to check files."
    NO: "The user wants a complex formal deliverable, so this is a Tier 2 document. I need a full workspace audit."

    RULES:
    - Always use "I" with contractions ("I'm", "I've", "I'll"). Never passive voice.
    - Name the section, field, or problem — never file names, paths, tool names, or internal labels.
    - Never mention tier numbers, classification labels, workflow step numbers, or internal terminology.
    - Write as if explaining your thinking to a colleague — clear, natural, jargon-free.
    - Max 3 sentences, 40 words. Over that — cut.

    Args:
        reflection: 2–3 sentences in first person. What I found, what I'm doing next and why. Max 40 words. No internal jargon.
    """