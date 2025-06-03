# Files API Guide for Excel & PDF Analysis

## Understanding How Files API Works with Claude Code Execution

The Files API allows you to upload files once and reference them across multiple conversations without re-uploading. This is perfect for your use case of analyzing Excel files with NZ tax guidelines.

### Key Concepts

1. **File Upload**: Upload files to get a unique `file_id`
2. **File Reference**: Use `file_id` in messages to reference files
3. **Persistence**: Files remain available until you delete them
4. **Code Integration**: Files work seamlessly with code execution tools

### Your Workflow: Excel Analysis with NZ Tax Guidelines

#### Step 1: Upload Your Files

```bash
# Start the enhanced script
python code-exec.py

# Upload your Excel files
/upload /path/to/financial_data_2024.xlsx
/upload /path/to/tax_calculations_2024.xlsx

# Upload your NZ tax PDF guidelines
/upload /path/to/nz_tax_guide_2024.pdf
/upload /path/to/ird_guidelines.pdf
/upload /path/to/business_tax_rules.pdf

# Check what you've uploaded
/files
```

#### Step 2: Reference Files in Your Analysis

When you want to analyze the data, you can:

**Option A: Attach specific files**
```bash
/attach financial_data_2024.xlsx
/attach nz_tax_guide_2024.pdf
Analyze this financial data according to NZ tax rules. Calculate the tax liability and identify any deductions.
```

**Option B: Reference files in your prompt**
```bash
Please analyze the uploaded Excel files (financial_data_2024.xlsx and tax_calculations_2024.xlsx) using the New Zealand tax guidelines from the uploaded PDF documents. Use the code execution tool to:

1. Load and examine the Excel data
2. Apply NZ tax calculations based on the PDF guidelines
3. Generate a tax analysis report
4. Identify potential tax savings or compliance issues

Make sure to reference the specific tax rates and rules mentioned in the PDFs.
```

#### Step 3: Advanced Analysis Prompts

```bash
# For comprehensive analysis
Using the uploaded files, create a Python analysis that:

1. **Data Processing**: Load both Excel files and extract key financial metrics
2. **Tax Rule Application**: Reference the NZ tax PDFs to identify applicable rules
3. **Calculations**: Compute tax liability, GST obligations, and deductions
4. **Compliance Check**: Cross-reference against IRD guidelines
5. **Report Generation**: Create a summary with recommendations

Please quote specific sections from the tax PDFs when explaining your calculations.
```

### File Types and How Claude Handles Them

#### Excel Files (.xlsx, .xls)
- Claude can read the structure and content
- Code execution tool can use pandas to analyze data
- Can process multiple sheets and complex formulas

#### PDF Documents (.pdf)
- Claude can extract text and understand document structure
- Can reference specific sections, tables, and rules
- Combines well with code analysis for rule application

### Best Practices for Your Use Case

#### 1. Organize Your Files
```bash
# Upload reference documents first
/upload /path/to/nz_tax_guide_2024.pdf
/upload /path/to/ird_business_rules.pdf

# Then upload data files
/upload /path/to/q1_financial_data.xlsx
/upload /path/to/q2_financial_data.xlsx
```

#### 2. Use Descriptive Prompts
```bash
Analyze Q1 financial data (q1_financial_data.xlsx) for a NZ business:

1. Extract revenue, expenses, and deductions from the Excel file
2. Apply the tax calculations described in nz_tax_guide_2024.pdf
3. Check compliance with IRD business rules from ird_business_rules.pdf
4. Generate Python code to automate these calculations
5. Provide a tax liability summary

Reference specific page numbers or sections from the PDFs when explaining tax rule applications.
```

#### 3. Iterative Analysis
```bash
# First: Get overview
Provide an overview of the financial data and applicable tax rules

# Then: Deep dive
Now perform detailed tax calculations using the code execution tool

# Finally: Optimization
Identify opportunities for tax optimization based on the uploaded guidelines
```

### Technical Details

#### File Upload Process
1. Files are uploaded to Anthropic's servers
2. You receive a unique `file_id` 
3. Files are associated with your API key/organization
4. Max file size: 500MB, Total storage: 100GB

#### Message Structure
When files are attached, the message looks like:
```json
{
  "role": "user",
  "content": [
    {
      "type": "text", 
      "text": "Analyze this data according to NZ tax rules"
    },
    {
      "type": "file",
      "file": {"file_id": "file_abc123"}
    },
    {
      "type": "file", 
      "file": {"file_id": "file_def456"}
    }
  ]
}
```

#### Code Execution Integration
- Claude can reference file content in Python code
- Can use libraries like `pandas`, `openpyxl` for Excel
- Can extract and process PDF content for rule application

### Example Complete Workflow

```bash
# 1. Start the tool
python code-exec.py

# 2. Upload all your files
/upload financial_data_2024.xlsx
/upload tax_calculations_2024.xlsx  
/upload nz_tax_guide_2024.pdf
/upload ird_guidelines.pdf

# 3. Check uploads
/files

# 4. Attach relevant files and start analysis
/attach financial_data_2024.xlsx
/attach nz_tax_guide_2024.pdf

Create a comprehensive NZ tax analysis:

1. Load the Excel data and show its structure
2. Extract key financial metrics (revenue, expenses, deductions)
3. Reference the NZ tax guide to identify applicable tax rates and rules
4. Calculate:
   - Income tax liability
   - GST obligations
   - Available deductions
   - Provisional tax requirements
5. Generate a formatted report with:
   - Tax calculations breakdown
   - Compliance status
   - Recommendations for optimization
6. Create reusable Python functions for future tax calculations

Please quote relevant sections from the tax guide when explaining calculations.
```

This approach allows you to build a comprehensive tax analysis system that combines your Excel data with authoritative NZ tax guidelines, all powered by Claude's code execution capabilities.