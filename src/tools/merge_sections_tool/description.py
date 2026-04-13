MERGE_SECTIONS_TOOL_DESCRIPTION = """
    Assemble multiple VFS section files into a single final document. This merges content
    server-side without loading it into your context — use it after parallel `task` calls
    to combine section outputs into one deliverable.

    The sections are concatenated in the order you specify. Missing sections are skipped
    and reported. The merged document is written to the output path in VFS.

    Args:
        section_paths: Ordered list of VFS paths to merge (e.g., ["/sections/01-intro.md", "/sections/02-site.md"]).
        output_path: VFS path for the final merged document (e.g., "/acme-ltd/reports/management-accounts-march.md").
        separator: Text inserted between sections. Default: "\\n\\n---\\n\\n"
        display_name: Short label for the UI. E.g., "Assembling management accounts report"
    """
