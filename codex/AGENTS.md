# Codex: rules when Claude delegates a task to you

These apply when a task arrives with a brief from Claude (GOAL / FILES YOU OWN / DONE WHEN). Project instructions, if any, take precedence.

- Work only on the files you were assigned. If you need to touch another one, stop and say so in your summary.
- No `git commit`, `git push` or branch changes: Claude reviews the diff and decides.
- Run the acceptance command before finishing and paste the last lines of its output.
- Do not read or print `.env` files, keys or tokens. Do not install new dependencies unless told to.
- If the specification is ambiguous, do not guess: list your questions and stop.
- Final answer of ≤10 lines: files changed, result of the acceptance command, open questions or risks. Do not repeat the code.
- Code and identifiers in English; explanations in the user's language.
