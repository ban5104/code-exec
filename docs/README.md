# Claude with Code Execution Tool

An interactive Python script that provides access to Claude with the code execution tool enabled.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your API key (if not already set):
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

3. Run the script:
   ```bash
   python code-exec.py
   ```

## Features

- Interactive chat with Claude
- Code execution tool enabled by default
- Conversation history maintained throughout session
- Built-in commands:
  - `/quit` or `/exit` - Exit the program
  - `/reset` - Clear conversation history
  - `/model <model_name>` - Change the model (e.g., `/model claude-sonnet-4-20250514`)
  - `/nocode` - Send next message without code execution
  - `/help` - Show help message

## Example Usage

```
👤 You: Calculate the fibonacci sequence up to the 10th number

🤖 Claude: I'll calculate the Fibonacci sequence up to the 10th number for you.

[Executing code...]

[Code Output]:
Fibonacci sequence up to the 10th number:
Position 1: 0
Position 2: 1
Position 3: 1
Position 4: 2
Position 5: 3
Position 6: 5
Position 7: 8
Position 8: 13
Position 9: 21
Position 10: 34

The 10th Fibonacci number is 34.
```

## Supported Models

- claude-opus-4-20250514 (default)
- claude-sonnet-4-20250514
- claude-sonnet-3-20241022
- claude-haiku-3-5-20241022