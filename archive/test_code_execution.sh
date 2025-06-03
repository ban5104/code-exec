#!/bin/bash

# Test the Anthropic code execution tool
curl https://api.anthropic.com/v1/messages \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "anthropic-beta: code-execution-2025-05-22" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-opus-4-20250514",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": "Calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
            }
        ],
        "tools": [{
            "type": "code_execution_20250522",
            "name": "code_execution"
        }]
    }'