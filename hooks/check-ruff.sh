#!/bin/bash
# Run ruff on Python files

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

[[ ! "$file_path" =~ \.py$ ]] && exit 0
[[ ! -f "$file_path" ]] && exit 0

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0

ruff_output=$(uv run --with ruff ruff check "$file_path" 2>/dev/null)
if [[ -n "$ruff_output" ]]; then
    issue_count=$(echo "$ruff_output" | grep -c "^" || echo "0")
    if [[ $issue_count -gt 0 ]]; then
        echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"<system-reminder>Ruff found issues. Run: uv run --with ruff ruff check --fix $file_path</system-reminder>\"}}"
    fi
fi

exit 0
