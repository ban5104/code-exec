# Dynamic Files API Usage Guide

## Working with Files Already in Your Anthropic Account

Perfect! Now you can work dynamically with any files in your Anthropic Files API account. Here's how to use your existing files:

### Step 1: Start the Enhanced Tool
```bash
python code-exec.py
```

### Step 2: List All Files in Your Account
```bash
/listapi
```
This will show you all files in your Anthropic account with their IDs, sizes, and upload dates.

### Step 3: Use Your Existing Files

#### Option A: Attach Files Directly by ID (Quickest)
```bash
# Attach your Swyftx Excel files directly
/attachid file_011CPhtTPzHHrsgxkbFpbKdU  # 2025 report
/attachid file_011CPhtSMZuKJKvqz84enVsW  # 2024 report  
/attachid file_011CPhsUu9dpm6VM5x3ntrfw  # Tax calculation PDF

# Now send your analysis request
Analyze my Swyftx cryptocurrency trading data for tax purposes. I need:

1. **Data Processing**: Load both Excel transaction reports (2024 and 2025)
2. **Tax Calculations**: Apply NZ cryptocurrency tax rules using the PDF guide
3. **Capital Gains**: Calculate capital gains/losses for each trade
4. **Tax Reporting**: Generate a tax-compliant summary for IRD

Use the code execution tool to process the Excel data and reference the PDF for tax rules.
```

#### Option B: Import for Repeated Use
```bash
# Import files into your session (gives them shorter names)
/import file_011CPhtTPzHHrsgxkbFpbKdU "Swyftx_2025.xlsx"
/import file_011CPhtSMZuKJKvqz84enVsW "Swyftx_2024.xlsx"
/import file_011CPhsUu9dpm6VM5x3ntrfw "Tax_Guide.pdf"

# Check what you have imported
/files

# Attach by simple names
/attach Swyftx_2025.xlsx
/attach Tax_Guide.pdf

# Send analysis request...
```

### Your Specific Files Usage

Based on your API response, here are your current files:

1. **Swyftx Transaction Report 2025** (`file_011CPhtTPzHHrsgxkbFpbKdU`) - 33.1 KB
2. **Swyftx 2024 Transaction Report** (`file_011CPhtSMZuKJKvqz84enVsW`) - 58.1 KB  
3. **Standard Form Calculation sheet TCEL** (`file_011CPhsUu9dpm6VM5x3ntrfw`) - 398.3 KB PDF

### Quick Start for Crypto Tax Analysis

```bash
# Start the tool
python code-exec.py

# List your files to see them formatted nicely
/listapi

# Attach all relevant files for crypto tax analysis
/attachid file_011CPhtTPzHHrsgxkbFpbKdU
/attachid file_011CPhtSMZuKJKvqz84enVsW  
/attachid file_011CPhsUu9dpm6VM5x3ntrfw

# Comprehensive crypto tax analysis
Analyze my Swyftx cryptocurrency transactions for NZ tax compliance:

**Files Attached:**
- Swyftx Transaction Report 2025.xlsx: Latest trading data
- Swyftx 2024 Transaction Report.xlsx: Previous year for comparison
- Standard_Form_Calculation sheet_TCEL.pdf: Tax calculation guidelines

**Required Analysis:**
1. **Data Extraction**: Load both Excel files and extract:
   - All buy/sell transactions
   - Transaction dates, amounts, prices
   - Fees and costs
   - Currency pairs traded

2. **Tax Calculations**: Apply NZ crypto tax rules:
   - Calculate capital gains/losses for each disposal
   - Apply FIFO (First In First Out) method
   - Account for transaction fees
   - Handle different crypto assets separately

3. **Compliance Reporting**: Generate:
   - Summary of total capital gains/losses
   - Detailed transaction log for IRD
   - Tax liability calculation
   - Any deductible expenses

4. **Year-over-Year Analysis**: Compare 2024 vs 2025:
   - Trading volume changes
   - Profit/loss trends
   - Tax implications

Please use the PDF guidelines for specific calculation methods and reference exact sections when explaining tax treatments.
```

### Advanced Workflows

#### Continuous Analysis (New Files)
```bash
# When you upload new files, just list and attach them
/listapi
/attachid <new_file_id>

# No need to modify the script - it works with any files in your account
```

#### Type-Based Analysis
```bash
# List files to see what you have
/listapi

# Import files with descriptive names by type
/import file_xyz123 "Q1_Trading_Data.xlsx"  
/import file_abc456 "Crypto_Tax_Rules_2025.pdf"
/import file_def789 "DeFi_Transactions.xlsx"

# Attach files by category for specific analysis
/attach Q1_Trading_Data.xlsx
/attach Crypto_Tax_Rules_2025.pdf

Analyze Q1 DeFi and traditional crypto trading for tax implications...
```

#### Multi-Period Analysis
```bash
# Import multiple years of data
/import file_2024_id "Crypto_2024.xlsx"
/import file_2025_id "Crypto_2025.xlsx"
/import file_2023_id "Crypto_2023.xlsx"

# Attach all for trend analysis
/attach Crypto_2023.xlsx
/attach Crypto_2024.xlsx  
/attach Crypto_2025.xlsx

Perform a 3-year crypto tax analysis showing trends and optimization opportunities...
```

### Commands Summary

| Command | Purpose | Example |
|---------|---------|---------|
| `/listapi` | Show all files in your account | `/listapi` |
| `/attachid <id>` | Attach file directly by ID | `/attachid file_011CPhtTPzHHrsgxkbFpbKdU` |
| `/import <id> <name>` | Import file with custom name | `/import file_011CPhtTPzHHrsgxkbFpbKdU "Swyftx_2025.xlsx"` |
| `/attach <name>` | Attach imported file | `/attach Swyftx_2025.xlsx` |
| `/files` | Show imported files | `/files` |

This approach gives you maximum flexibility to work with any files in your account without hardcoding anything in the script!