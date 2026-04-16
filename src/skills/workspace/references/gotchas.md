# Workspace Gotchas

- Do not start project or task writes until the workspace is resolved.
- Do not assume the current UI workspace matches the API context if the runtime context is empty.
- Do not ask the user to restate member information that can be read from `members`.
- If multiple members have similar names, ask for the minimum detail needed to disambiguate.
- Treat workspace switching as a real context change; update scratchpad notes immediately.
