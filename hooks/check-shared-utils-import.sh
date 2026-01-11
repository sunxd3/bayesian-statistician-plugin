#!/bin/bash
# Warn if experiment Python file doesn't import shared_utils

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

[[ ! "$file_path" =~ \.py$ ]] && exit 0
[[ ! "$file_path" =~ experiments/ ]] && exit 0
[[ ! -f "$file_path" ]] && exit 0

if ! grep -q "from shared_utils import\|import shared_utils" "$file_path"; then
    echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"<system-reminder>Not importing from shared_utils. Use shared utilities instead of rewriting common patterns.</system-reminder>\"}}"
fi

exit 0
