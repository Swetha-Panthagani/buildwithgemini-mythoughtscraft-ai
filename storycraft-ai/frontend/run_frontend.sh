#!/usr/bin/env bash
set -e

export AGENT_ENGINE_RESOURCE_NAME="projects/766341849093/locations/us-east1/reasoningEngines/8535814430657609728"
export AGENT_DIRECTORY="app"
export PORT="${PORT:-8085}"

echo "Starting frontend proxy on port $PORT..."
echo "AGENT_ENGINE_RESOURCE_NAME: $AGENT_ENGINE_RESOURCE_NAME"
echo "AGENT_DIRECTORY: $AGENT_DIRECTORY"

exec .venv_frontend/bin/python main.py
