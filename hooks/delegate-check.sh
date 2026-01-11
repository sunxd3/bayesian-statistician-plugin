#!/bin/bash
# PostToolUse hook - remind orchestrating agent to delegate

input=$(cat)
tool=$(echo "$input" | jq -r '.tool_name')

reminder=""

case "$tool" in
  Bash)
    cmd=$(echo "$input" | jq -r '.tool_input.command')
    if [[ "$cmd" =~ ^(uv|python)[[:space:]] ]]; then
      reminder="<system-reminder>[Orchestrator - ignore if you lack Task tool] Delegate script execution to specialized subagents. Only run essential orchestration commands directly.</system-reminder>"
    fi
    ;;
  Write|Edit)
    path=$(echo "$input" | jq -r '.tool_input.file_path')
    if [[ "$path" =~ \.(stan|py)$ ]]; then
      reminder="<system-reminder>[Orchestrator - ignore if you lack Task tool] Delegate .py/.stan writing to specialized subagents (eda-analyst, model-fitter, etc.). Only write orchestration files (log.md, plans) directly.</system-reminder>"
    fi
    ;;
esac

# Output additionalContext (non-blocking). Subagents will ignore this as they lack Task tool.
if [[ -n "$reminder" ]]; then
  echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"$reminder\"}}"
fi

exit 0
