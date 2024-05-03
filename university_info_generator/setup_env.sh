#!/bin/bash

# # Environment Variables
current_path=$(pwd)

# Get the parent directory of the current directory
parent_dir=$(dirname "$current_path")

# Set PROJECT_HOME to the parent directory
export PROJECT_HOME="$parent_dir"

# Optionally, print PROJECT_HOME to verify it's set correctly
export PYTHONPATH="$PROJECT_HOME:$PYTHONPATH"

# Configuration specific to the project
export CONFIG_PATH="$PROJECT_HOME/university_info_generator/config"
export API_KEY_PATH="$CONFIG_PATH/uforseAdminKey.json"
export CACHE_REPO_PATH="$PROJECT_HOME/cache_repo"

# Check if the directory does not exist
if [ ! -d "$CACHE_REPO_PATH" ]; then
    # Directory does not exist, so create it
    mkdir -p "$CACHE_REPO_PATH"
    echo "Created directory: $CACHE_REPO_PATH"
else
    echo "Directory already exists: $CACHE_REPO_PATH"
fi

# langchain env setup
export LANGCHAIN_TRACING_V2="true"
# TODO: be careful
export LANGCHAIN_API_KEY="ls__3780df60c0ef4fd2b2414f032feb31ce"

echo "Environment variables set:"
echo "PROJECT_HOME=$PROJECT_HOME"
echo "PYTHONPATH=$PYTHONPATH"
echo "API_KEY_PATH=$PROJECT_HOME"
echo "CACHE_REPO_PATH=$CACHE_REPO_PATH"
echo "LANGCHAIN_API_KEY=$LANGCHAIN_API_KEY"

echo "Environment set up for uni_info_generator"
