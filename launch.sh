#!/bin/bash

# Load all keys from .env
source .env 2>/dev/null
export $(grep -v '^#' .env | xargs) 2>/dev/null

# Collect all keys
KEYS=()
for i in $(seq 1 15); do
    if [ $i -eq 1 ]; then
        KEY_VAR="GOOGLE_API_KEY"
    else
        KEY_VAR="GOOGLE_API_KEY_$i"
    fi
    KEY_VAL="${!KEY_VAR}"
    if [[ $KEY_VAL == AIza* ]]; then
        KEYS+=("$KEY_VAL")
    fi
done

echo "Found ${#KEYS[@]} API keys"

KEY_INDEX=0

while true; do
    CURRENT_KEY="${KEYS[$KEY_INDEX]}"
    echo "Starting ADK with key $((KEY_INDEX+1))/${#KEYS[@]} (...${CURRENT_KEY: -6})"
    
    export GOOGLE_API_KEY="$CURRENT_KEY"
    unset GOOGLE_GENAI_USE_VERTEXAI
    
    # Run ADK and capture exit
    PYTHONPATH=/home/saiashribad05/multi-agent-system \
        .venv/bin/adk web . \
        --host 0.0.0.0 \
        --port 8000 \
        --allow_origins "*" &
    
    ADK_PID=$!
    
    # Monitor for 429 errors
    while kill -0 $ADK_PID 2>/dev/null; do
        sleep 5
    done
    
    # Rotate to next key
    KEY_INDEX=$(( (KEY_INDEX + 1) % ${#KEYS[@]} ))
    echo "Switching to next key..."
    sleep 2
done
