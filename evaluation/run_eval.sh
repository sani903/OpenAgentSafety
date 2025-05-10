#!/bin/bash

# Exit on any error would be useful for debugging
#if [ -n "$DEBUG" ]; then
#set -e
#fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$(basename "$SCRIPT_DIR")" != "evaluation" ]; then
    echo "Error: Script must be run from the 'evaluation' directory"
    echo "Current directory is: $(basename "$SCRIPT_DIR")"
    exit 1
fi

TASKS_DIR="$(cd "$SCRIPT_DIR/../workspaces/tasks" && pwd)"

# AGENT_LLM_CONFIG is the config name for the agent LLM
# In config.toml, you should have a section with the name
# [llm.<AGENT_LLM_CONFIG>], e.g. [llm.agent]
AGENT_LLM_CONFIG="three"

# ENV_LLM_CONFIG is the config name for the environment LLM,
# used by the NPCs and LLM-based evaluators.
# In config.toml, you should have a section with the name
# [llm.<ENV_LLM_CONFIG>], e.g. [llm.env]
ENV_LLM_CONFIG="base"

# OUTPUTS_PATH is the path to save trajectories and evaluation results
OUTPUTS_PATH="o3-mini"

# SERVER_HOSTNAME is the hostname of the server that hosts all the web services,
# including RocketChat, ownCloud, GitLab, and Plane.
SERVER_HOSTNAME="localhost"

# VERSION is the version of the task images to use
# If a task doesn't have a published image with this version, it will be skipped
# 12/15/2024: this is for forward compatibility, in the case where we add new tasks
# after the 1.0.0 release
VERSION="1.0"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --agent-llm-config)
            AGENT_LLM_CONFIG="$2"
            shift 2
            ;;
        --env-llm-config)
            ENV_LLM_CONFIG="$2"
            shift 2
            ;;
        --outputs-path)
            OUTPUTS_PATH="$2"
            shift 2
            ;;
        --server-hostname)
            SERVER_HOSTNAME="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# Convert outputs_path to absolute path
if [[ ! "$OUTPUTS_PATH" = /* ]]; then
    # If path is not already absolute (doesn't start with /), make it absolute
    OUTPUTS_PATH="$(cd "$(dirname "$OUTPUTS_PATH")" 2>/dev/null && pwd)/$(basename "$OUTPUTS_PATH")"
fi

echo "Using agent LLM config: $AGENT_LLM_CONFIG"
echo "Using environment LLM config: $ENV_LLM_CONFIG"
echo "Outputs path: $OUTPUTS_PATH"
echo "Server hostname: $SERVER_HOSTNAME"
# skip_until_match=true
RESTART_EVERY=1
TASK_COUNT=0
TMUX_SESSION="uv2"
TMUX_COMMAND="uv run fastapi run sotopia/api/fastapi_server.py --workers 1 --port 8080"
# Iterate through each directory in tasks
for task_dir in "$TASKS_DIR"/*/; do
    task_name=$(basename "$task_dir")

    if [[ "$task_name" != *safety* ]]; then
        echo "Skipping $task_name - non-safety-related task"
        continue
    fi

    # if [ "$skip_until_match" = true ]; then
    #     if [[ "$task_name" == *safety*paper*trail* ]]; then
    #         skip_until_match=false
    #     else
    #         echo "Skipping $task_name - before safety*finance*update* match"
    #         continue
    #     fi
    # fi
    # Check if evaluation file exists
    echo $task_name
    if [ -f "$OUTPUTS_PATH/eval_${task_name}.json" ]; then
        echo "Skipping $task_name - evaluation file already exists"
        continue
    fi
    
    echo "Running evaluation for task: $task_name"
    # FIXME: pleae change this task image name like shown below if you are building images locally
#    task_image="${task_name}:latest"
    # task_image="ghcr.io/sani903/${task_name}-image:${VERSION}"
    # echo "Use released image $task_image..."
    
    # Run evaluation from the evaluation directory
    cd "$SCRIPT_DIR"
    /home/ubuntu/.local/bin/poetry run python run_eval.py \
        --agent-llm-config "$AGENT_LLM_CONFIG" \
        --env-llm-config "$ENV_LLM_CONFIG" \
        --outputs-path "$OUTPUTS_PATH" \
        --server-hostname "$SERVER_HOSTNAME" \
        --task-path "$task_dir"
    ((TASK_COUNT++))
    if (( TASK_COUNT % RESTART_EVERY == 0 )); then
        echo "🔁 Restarting tmux process in session: $TMUX_SESSION"
        tmux send-keys -t "$TMUX_SESSION" C-c
        sleep 1
        tmux send-keys -t "$TMUX_SESSION" "$TMUX_COMMAND" C-m
    fi

done

echo "All evaluation completed successfully!"
