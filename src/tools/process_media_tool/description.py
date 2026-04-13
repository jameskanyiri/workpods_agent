PROCESS_MEDIA_TOOL_DESCRIPTION = """\
Retrieve and process a media file (image, document, or audio) that a user sent \
via WhatsApp. Call this tool when the user's message indicates they uploaded media \
and you need to view, read, or analyze its contents.

The tool downloads the file from WhatsApp's servers, converts it to base64, and \
returns it as a multimodal content block that you can interpret directly.

Parameters:
- media_id: The WhatsApp media ID from the incoming message metadata.
- mime_type: The MIME type of the media (e.g. "image/jpeg", "application/pdf", "audio/ogg").
- instruction: What you want the tool to do with the media (e.g. "Extract all line items and totals from this receipt", "Summarize this financial report", "Read and extract data from this invoice").
- filename: The original filename of the media (e.g. "report.pdf"). Defaults to "document" if not provided.
"""
