---
name: validation-protocol
description: Standard input validation for subagents — two-step check (arguments, filesystem), strict single-line [EXCEPTION] output on failure.
user-invocable: false
---

# Validation Protocol

Validate inputs FIRST, before any other work. The agent body declares its
specific args and filesystem checks under `## Interface > Input`; this protocol
defines how to perform the checks and what to return on failure.

The protocol covers **existence and presence** only. Malformed inputs (corrupt
data, wrong format, unreadable file) are agent-body discretion — abort with an
`[EXCEPTION]` and an informative label, or proceed if the input is salvageable.

## Step 1 — Arguments

Verify the input prompt contains every **required** argument from your
`**Args:**` line. Arguments marked with `?` (e.g., `focus_area?: Text`) are
optional — their absence is not a failure. If a required argument is missing or
ambiguous, return ONLY:

`[EXCEPTION] InvalidInput: Missing '<name>'. Expected: <what it should be>.`

## Step 2 — Filesystem

Use `ls` (via the Bash tool) to verify the paths listed in your
`**Filesystem (...):**` line(s). Choose the exception type by source:

- **Direct input path missing.** Return `[EXCEPTION] PreconditionFailed: '<path>' does not exist.`
- **Upstream artifact missing** (a file produced by a prior phase/subagent). Return `[EXCEPTION] DependencyMissing: '<path>' — <reason>.`

## Stop rule

Return the single `[EXCEPTION]` line and nothing else — no explanations, no
suggestions, no follow-up questions. Stop immediately.
