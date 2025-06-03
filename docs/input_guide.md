# Multi-line Input Guide

## Enhanced Input Options

The script now supports multiple ways to input text, including proper multi-line pasting!

### 1. **Single Line Input** (Default)
Just type normally and press Enter:
```
👤 You: Analyze my crypto data
```

### 2. **Multi-line Input Mode**
Type `/multiline` to enter multi-line mode:
```
👤 You: /multiline

👤 You (paste your text, then press Ctrl+D on a new line to finish):
Analyze my Swyftx cryptocurrency transactions for NZ tax compliance.

Please process both Excel files:
1. Extract all buy/sell transactions
2. Calculate capital gains using FIFO method
3. Apply NZ tax rates
4. Generate tax report

Use the attached PDF for specific tax rules.
[Press Ctrl+D here to finish]
```

### 3. **Direct Multi-line Pasting**
When you paste multi-line content directly, the script automatically detects it:
- Paste your content (Right-click → Paste or Ctrl+Shift+V)
- Press Ctrl+D when done

### 4. **Clipboard Paste Command**
Type `/paste` to paste from your system clipboard:
```
👤 You: /paste
📋 Pasted 245 characters from clipboard
```

### 5. **Standard Terminal Pasting**
Most terminals support:
- **Right-click** → Paste
- **Ctrl+Shift+V** (Linux/Windows terminals)
- **Cmd+V** (Mac terminals)

## Practical Usage for Your Crypto Analysis

### Example 1: Quick Analysis
```bash
👤 You: /attachid file_011CPhtTPzHHrsgxkbFpbKdU
📎 File 'Swyftx Transaction Report 2025 - Excel.xlsx' will be attached to your next message

👤 You: Analyze this crypto data for tax purposes
```

### Example 2: Detailed Multi-line Request
```bash
👤 You: /multiline

👤 You (paste your text, then press Ctrl+D on a new line to finish):
I need a comprehensive cryptocurrency tax analysis for my NZ tax return.

**Files to analyze:**
- 2025 Swyftx transaction report (already attached)
- 2024 Swyftx transaction report 
- NZ tax calculation guidelines PDF

**Required analysis:**
1. **Transaction Processing:**
   - Load both Excel files
   - Clean and validate transaction data
   - Identify all crypto assets traded

2. **Tax Calculations:**
   - Apply FIFO method for capital gains
   - Calculate disposal events and costs
   - Account for transaction fees
   - Apply NZ tax rates (28% for companies, progressive for individuals)

3. **Reporting:**
   - Generate detailed transaction log
   - Summary of total gains/losses
   - Tax liability calculation
   - Compliance checklist for IRD submission

Please reference specific sections from the tax guide PDF when explaining calculations.
[Ctrl+D to finish]
```

### Example 3: Pasting Long Requirements
If you have detailed requirements copied from a document:
```bash
👤 You: /paste
📋 Pasted 1,247 characters from clipboard
```

## Tips for Better Input

### 1. **For Complex Analysis Requests:**
- Use `/multiline` for detailed, structured requests
- Break down requirements into numbered sections
- Specify exactly what files to use

### 2. **For Quick Questions:**
- Use single-line input for simple commands
- Commands like `/listapi`, `/help`, `/files` work normally

### 3. **When Pasting from Documents:**
- Copy your requirements from Word/Google Docs
- Use `/paste` command for clean insertion
- Or paste directly and press Ctrl+D

### 4. **Terminal Compatibility:**
- Works in WSL, Linux terminals, Mac Terminal
- Windows Command Prompt and PowerShell supported
- VS Code integrated terminal works well

## Keyboard Shortcuts Summary

| Action | Shortcut | Description |
|--------|----------|-------------|
| **Finish multi-line** | `Ctrl+D` | Complete multi-line input |
| **Cancel input** | `Ctrl+C` | Cancel current input |
| **Terminal paste** | `Ctrl+Shift+V` | Standard terminal paste |
| **Terminal paste** | `Right-click` | Context menu paste |
| **Multi-line mode** | `/multiline` | Switch to multi-line input |
| **Clipboard paste** | `/paste` | Paste from system clipboard |

This makes it much easier to paste long, detailed analysis requests for your crypto tax work!