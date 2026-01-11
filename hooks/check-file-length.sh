#!/bin/bash
# Warn if Python file is too long

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

[[ ! "$file_path" =~ \.py$ ]] && exit 0
[[ ! -f "$file_path" ]] && exit 0

line_count=$(wc -l < "$file_path")
if [[ $line_count -gt 150 ]]; then
    echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"<system-reminder>File is $line_count lines. Consider splitting into smaller modules.</system-reminder>\"}}"
fi

exit 0
