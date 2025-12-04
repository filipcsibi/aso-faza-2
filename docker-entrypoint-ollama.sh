#!/bin/bash
set -e

# Start Ollama server in background
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
sleep 5

# Pull the model if not already present
echo "Pulling qwen2.5:7b model..."
ollama pull qwen2.5:7b

echo "Ollama is ready with qwen2.5:7b model"

# Keep the container running
wait
