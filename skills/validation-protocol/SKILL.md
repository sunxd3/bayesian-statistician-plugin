---
name: validation-protocol
description: Standard input validation for subagents — two-step check (arguments, filesystem), strict single-line [EXCEPTION] output on failure.
user-invocable: false
---

# Validation Protocol

Validate inputs FIRST, before any other work. Your agent body declares the specific args and filesystem checks under `## Input Validation`; this protocol defines how to perform the checks and what to return on failure.

## Step 1 — Arguments

Verify the orchestrator's prompt contains every **required** argument from your `Args` entry under `## Interface > Input` (or equivalent). Arguments marked with `?` (e.g., `focus_area?: Text`) are optional — their absence is not a failure. If a required argument is missing or ambiguous, return ONLY:

`[EXCEPTION] InvalidInput: Missing '<name>'. Expected: <what it should be>.`

## Step 2 — Filesystem

Use `ls` (via the Bash tool) to verify the paths listed in your validation section. Choose the exception type by source:

- **Direct input path missing** → `[EXCEPTION] PreconditionFailed: '<path>' does not exist.`
- **Upstream artifact missing** (a file produced by a prior phase/subagent) → `[EXCEPTION] DependencyMissing: '<path>' — <reason>.`

## Stop rule

Return the single `[EXCEPTION]` line and nothing else — no explanations, no suggestions, no follow-up questions. Stop immediately.
