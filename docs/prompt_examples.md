# Effective Prompts for Excel + PDF Analysis

## How to Reference Multiple File Types in Your Prompts

### 1. Basic Multi-File Analysis

```bash
# After uploading financial_data.xlsx and nz_tax_guide.pdf
/attach financial_data.xlsx
/attach nz_tax_guide.pdf

Please analyze the financial data in the Excel file according to the tax rules in the PDF. Use Python to:
1. Load and explore the Excel data structure
2. Extract key financial figures
3. Apply relevant tax calculations based on the PDF guidelines
4. Show your work with clear references to both files
```

### 2. Comprehensive Tax Analysis

```bash
# With multiple Excel files and PDF guidelines
/attach q1_data.xlsx
/attach q2_data.xlsx  
/attach nz_tax_guide.pdf
/attach ird_business_rules.pdf

I need a complete NZ tax analysis for my business. The Excel files contain quarterly financial data. Please:

**Phase 1: Data Understanding**
- Load both Excel files and show their structure
- Identify key financial metrics across quarters
- Summarize total revenue, expenses, and deductions

**Phase 2: Tax Rule Application**
- Reference the NZ tax guide to identify applicable business tax rates
- Use IRD business rules to determine compliance requirements
- Quote specific sections when explaining tax applications

**Phase 3: Calculations & Compliance**
- Calculate quarterly and annual tax liability
- Determine GST obligations and filing requirements  
- Identify available deductions and tax credits
- Check for provisional tax requirements

**Phase 4: Optimization & Reporting**
- Suggest tax optimization strategies based on the guidelines
- Generate a formatted tax report
- Create Python functions for ongoing tax calculations

Please include specific page/section references from the PDFs in your analysis.
```

### 3. Specific Tax Scenario Analysis

```bash
/attach expense_report.xlsx
/attach depreciation_schedule.xlsx
/attach nz_depreciation_guide.pdf

I need help with depreciation calculations for tax purposes:

1. **Asset Analysis**: Extract asset information from both Excel files
2. **Rule Application**: Use the NZ depreciation guide to determine:
   - Applicable depreciation rates for each asset category
   - Methods allowed (diminishing value vs straight line)
   - Special rules for different asset types
3. **Calculations**: Generate Python code to calculate:
   - Annual depreciation deductions
   - Book vs tax depreciation differences
   - Impact on tax liability
4. **Compliance**: Ensure calculations meet IRD requirements from the guide

Reference specific tables or sections from the depreciation guide.
```

### 4. Comparative Analysis Across Periods

```bash
/attach 2023_financials.xlsx
/attach 2024_financials.xlsx
/attach tax_law_changes_2024.pdf

Perform a year-over-year tax analysis considering law changes:

1. **Data Comparison**: Compare financial metrics between 2023 and 2024
2. **Law Changes**: Identify new tax rules from the 2024 changes document
3. **Impact Analysis**: Calculate how law changes affect tax liability
4. **Strategic Planning**: Recommend actions based on the changes
```

### 5. GST and Income Tax Combined Analysis

```bash
/attach sales_data.xlsx
/attach purchase_records.xlsx
/attach nz_gst_guide.pdf
/attach income_tax_rules.pdf

I need both GST and income tax analysis:

**GST Analysis** (using sales_data.xlsx, purchase_records.xlsx, nz_gst_guide.pdf):
- Calculate GST on sales and purchases
- Determine net GST position
- Check for GST registration thresholds
- Identify any zero-rated or exempt supplies

**Income Tax Analysis** (using all files):
- Calculate taxable income after GST considerations
- Apply income tax rates from the rules document
- Consider timing differences between GST and income tax
- Generate combined compliance report
```

## Best Practices for Multi-File Prompts

### 1. Be Explicit About File Relationships
```bash
# Good
Use the financial data from Q1_data.xlsx and apply the tax rates found in Table 3.2 of the NZ Tax Guide PDF.

# Better  
From Q1_data.xlsx, extract the 'Total Revenue' from cell B15 and apply the 28% company tax rate specified on page 23 of the NZ Tax Guide PDF.
```

### 2. Structure Your Requests
```bash
**Data Sources**: 
- financial_data.xlsx: Contains monthly P&L data
- nz_tax_guide.pdf: Official IRD tax rates and rules

**Required Analysis**:
1. [Specific task using Excel data]
2. [Tax rule application from PDF]
3. [Combined analysis and reporting]

**Expected Output**:
- Python code showing calculations
- Summary table with tax liability
- References to specific PDF sections used
```

### 3. Request Specific Citations
```bash
For each tax calculation, please cite:
- The specific page/section from the PDF where the rule is found
- The exact cell/range from the Excel file where data originates
- Any assumptions made in applying the rules

This helps ensure accuracy and allows for verification.
```

### 4. Ask for Verification Steps
```bash
After completing the analysis, please:
1. Create verification formulas to double-check key calculations
2. Compare results against examples in the PDF (if any)
3. Identify any data quality issues in the Excel files
4. Suggest additional checks for compliance
```

### 5. Request Reusable Code
```bash
Please structure your Python code as reusable functions:

```python
def calculate_nz_company_tax(revenue, expenses, tax_guide_rates):
    """Calculate NZ company tax based on IRD guidelines"""
    # Implementation here
    
def process_excel_financials(file_path):
    """Extract and clean financial data from Excel"""
    # Implementation here

def generate_tax_report(financial_data, tax_calculations):
    """Generate formatted tax compliance report"""  
    # Implementation here
```

This allows for easy reuse with future financial data.
```

## Advanced Integration Techniques

### 1. Cross-Reference Validation
```bash
Use the Excel data to validate examples in the PDF:
1. Find calculation examples in the tax guide PDF
2. Recreate those calculations using similar data from Excel
3. Compare results to ensure understanding is correct
4. Apply the validated approach to the full dataset
```

### 2. Scenario Modeling
```bash
Using the base financial data and tax rules, create scenarios:
1. **Current Scenario**: Apply existing tax rules to current data
2. **Optimization Scenario**: Implement suggestions from the PDF
3. **Growth Scenario**: Model tax impact of 20% revenue growth
4. **Comparison Table**: Show tax implications of each scenario
```

### 3. Automated Compliance Checking
```bash
Create a compliance checklist based on the PDF guidelines:
1. Extract all compliance requirements from the PDFs
2. Check Excel data against each requirement
3. Flag any potential compliance issues
4. Suggest data collection or process improvements
```

These prompting techniques will help you get the most accurate and useful analysis from your Excel and PDF files using Claude's code execution capabilities.