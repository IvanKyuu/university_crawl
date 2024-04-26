#!/bin/bash

# Environment Variables
export PROJECT_HOME="/home/ivan/Uforse/uni_info_generator"
export PYTHONPATH="$PROJECT_HOME:$PYTHONPATH"

# Configuration specific to the project
export CONFIG_PATH="$PROJECT_HOME/university_info_generator/config"
export API_KEY_PATH="$CONFIG_PATH/uforseAdminKey.json"
export CACHE_REPO_PATH="$PROJECT_HOME/cache_repo"

echo "Environment variables set:"
echo "PROJECT_HOME=$PROJECT_HOME"
echo "PYTHONPATH=$PYTHONPATH"
echo "API_KEY_PATH=$PROJECT_HOME"
echo "CACHE_REPO_PATH=$CACHE_REPO_PATH"

# langchain env setup
export LANGCHAIN_TRACING_V2="true"
# TODO: be careful
export LANGCHAIN_API_KEY="ls__3780df60c0ef4fd2b2414f032feb31ce"


echo "Environment set up for uni_info_generator"
