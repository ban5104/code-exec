# Plan: Integrating AI Agent (Code Execution Assistant) with Microsoft Teams Bot

**Project Goal:** Create a Microsoft Teams bot that acts as a front-end for your existing Python script (`code-exec.py`). The bot will handle user messages and file attachments, pass them to the Anthropic API (and code execution tool if needed), and then present the results back to the user in Teams, styled according to the provided template guidelines.

---

## Phase 1: Refactor Core Python Logic

*Objective: Decouple the core processing logic from the command-line interface (`rich`) and make it callable as a library or service.*

**Location:** Modified `code-exec.py` (or a new set of Python modules derived from it, e.g., `claude_core.py`).

**Tasks:**

1.  **Isolate UI Elements:**
    * Identify all code related to `rich` (Console, Panel, Table, Syntax, etc.).
    * Modify functions that currently print to the console. Instead of printing, these functions should **return structured data** (e.g., dictionaries, lists of objects, custom classes).
    * For example, `claude.chat()` should return a dictionary containing the assistant's message, any executed code, output (including paths to any generated graphs/figures), errors, and web search results, rather than printing them.
    * The `list_files`, `list_web_searches`, `list_file_usage` functions should return the data they would display, not the `rich` Table objects.

2.  **Adapt Core Class (`ClaudeWithCodeExecution`):**
    * The constructor `__init__` might no longer need the `console` or `theme` parameters if all `rich` usage is removed or made optional.
    * Ensure methods like `upload_file`, `delete_file`, and the main `chat` method can be called programmatically without user interaction from the terminal.
    * The `chat` method will be central. It should accept:
        * `user_input: str`
        * `use_code_execution: bool`
        * `file_attachments_info: list` (List of dictionaries, e.g., `{'file_id': 'anthropic_file_id', 'file_name': 'example.txt'}`).
    * The `chat` method should return a structured response, for example:
        ```python
        {
            "assistant_message": "The main text response from Claude.",
            "tool_used": "code_execution" or "web_search" or None,
            "executed_code": "if tool_used == 'code_execution': ...",
            "code_output": "if tool_used == 'code_execution': ...", # Textual output
            "generated_figures": [ # List of paths/URLs to image files if tool_used == 'code_execution'
                {"figure_name": "graph1.png", "path_or_url": "/path/to/graph1.png"}
            ],
            "code_errors": "if tool_used == 'code_execution': ...",
            "web_searches": [ # if tool_used == 'web_search' or Claude used search
                {"query": "...", "results": [{"title": "...", "url": "...", "published": "..."}]}
            ],
            "files_accessed": [{"file_name": "...", "action": "..."}] # From your existing tracking
        }
        ```

3.  **File Handling Logic:**
    * Adapt `upload_file`: In Teams, files are uploaded to Teams first. Your bot will download them, then upload them to Anthropic.
    * The `uploaded_files` dictionary remains useful for tracking files sent to Anthropic.
    * If code execution generates image files (graphs/figures), ensure these are saved to a location accessible by the bot for embedding in the report.

4.  **Configuration Management:**
    * Load API keys and model configurations securely (e.g., from environment variables in Azure).

**Sections in Main Python Script (Core Logic - `claude_core.py`):**

* All Anthropic API interaction logic.
* Code execution tool invocation and result parsing (including handling paths to generated image files).
* Web search result parsing.
* File upload/management with Anthropic.
* Conversation history management (if kept server-side for context).
* The core `ClaudeWithCodeExecution` class and its methods, modified to return data.

---

## Phase 2: Microsoft Teams Bot Development

*Objective: Build the bot framework that receives user interactions from Teams and communicates with your refactored core logic.*

**Location:** New Python files (e.g., `app.py` or `bot.py` using a framework like `aiohttp` with `botbuilder-core` and `botbuilder-schema`, or Azure Functions).

**Tasks:**

1.  **Set up Bot Framework:**
    * Choose a Python bot framework (e.g., `botbuilder-python` SDK).
    * Create an Azure Bot resource.

2.  **Handle Incoming Messages:**
    * Implement an activity handler for incoming text messages.
    * Extract user text.

3.  **Handle File Attachments:**
    * Implement logic to detect and download file attachments from Teams.
    * Use the refactored `claude_core.upload_file()` to send files to Anthropic.

4.  **Manage Conversation State (Optional but Recommended):**
    * Store conversation history or user-specific context (e.g., Azure Blob Storage, Cosmos DB).

5.  **Call Core Logic:**
    * Instantiate your refactored `ClaudeWithCodeExecution` class.
    * Pass user messages and Anthropic `file_id`s to `claude_core.chat()`.
    * Determine if code execution is needed.

6.  **Error Handling:**
    * Implement robust error handling. Send user-friendly error messages to Teams.

**Sections in Bot-Specific Files (e.g., `bot.py`):**

* Bot activity handlers (on_message, on_file_upload).
* Teams authentication and communication.
* Downloading files from Teams.
* Orchestration of calls to `claude_core`.
* Passing results from `claude_core` to the UI/UX formatting layer.
* Logic to make generated figures (images) accessible via a URL if they need to be embedded from a path.

---

## Phase 3: Teams UI/UX Implementation

*Objective: Format the responses from your core logic for display within the Microsoft Teams interface, adhering to the specified report style.*

**Location:** New Python files (e.g., `teams_formatter.py`) and potentially JSON template files for Adaptive Cards or HTML/CSS templates for Tabs.

**Tasks:**

1.  **Simple Text Responses:**
    * If the core logic returns a simple `assistant_message` and no tools were used, format this as a plain text message for Teams (supports Markdown).

2.  **Report Formatting (Adaptive Cards or Teams Tab with Web Content):**
    * **Report Structure (Inspired by `Standard_Form_Calculation sheet_TCEL.pdf` [cite: 1, 2]):**
        * The report should aim to replicate the structure of the provided PDF template. This includes:
            * **Header Section:** Containing fixed information, similar to "TC TASMAN CONSULTING ENGINEERS" details[cite: 1, 2]. This could be configurable or a static part of the card/page.
            * **Job/Project Details Section:** Key-value pairs for information like:
                * `Description of Work:` (Populated by user query or bot context)
                * `Client:` (If applicable, from context)
                * `Job Reference:` (Generated or from context)
                * `Date:` (Current date/time of report generation)
                * `Project:` (User query or bot context)
                * `File Ref:` (If applicable)
                * `By:` (Bot name, e.g., "Code Execution Assistant")
            * **Main Content Section:** This is where the results from the Anthropic API will go.
                * Assistant's summary message.
                * Executed Python script (displayed in a code block).
                * Results/Output (textual).
                * **Graphs and Figures:** Embed any images (e.g., `generated_figures` from the core logic response) directly into the report. Adaptive Cards use an `Image` element; HTML uses `<img>`.
                * Errors (if any), displayed clearly.
    * **Sources Section (at the bottom):**
        * A dedicated section titled "Sources".
        * For each web source used (from `web_searches` in the core logic response):
            * Display the source `title`.
            * Display the `url` as a clickable link.
            * Display the `published` date.
    * **Implementation Choice:**
        * **Adaptive Cards:** Suitable for moderately complex layouts. You'll define a JSON structure with elements like `TextBlock`, `ColumnSet`, `Image`, `FactSet` to mimic the PDF's sections. Use the [Adaptive Cards Designer](https://adaptivecards.io/designer/) for prototyping.
        * **Teams Tab with Web Content (HTML/CSS):** Offers maximum flexibility for styling if a very high-fidelity match to the PDF template (including specific fonts, branding, or complex layouts) is critical. Your Python bot backend (e.g., using Flask/Django) would serve this HTML page.
    * Create Python functions that take the structured response from `claude_core.chat()` and dynamically generate the Adaptive Card JSON or the HTML for the report page.

3.  **Sending Responses to Teams:**
    * Use the Teams Bot SDK to send the formatted text message or the Adaptive Card JSON (or a link to the Tab) as a reply to the user.

**Sections in UI/UX Files (e.g., `teams_formatter.py`, `adaptive_card_templates/`, `html_templates/`):**

* Functions to generate Adaptive Card JSON or HTML for reports, incorporating the template structure, figures, and sources section.
    * `def create_detailed_report_card(data, job_details): -> dict`
    * `def create_detailed_report_html(data, job_details): -> str`
* Functions to format simple text messages with Teams Markdown.
* (Potentially) JSON template files for Adaptive Cards or HTML/CSS template files.

---

## Phase 4: Deployment and Integration

1.  **Azure Deployment:**
    * Deploy your Python bot application to an Azure service (e.g., Azure App Service, Azure Functions). Ensure any generated image files are stored in a location accessible by the bot for embedding or serving.
    * Configure environment variables.
2.  **Bot Registration & Configuration:**
    * Connect your Azure Bot resource to the deployed application endpoint.
    * Enable the Microsoft Teams channel.
3.  **Testing:**
    * Thoroughly test in Teams:
        * Simple messages.
        * Messages with file attachments.
        * Requests triggering code execution that produces text and figures.
        * Requests triggering web searches.
        * Report structure and content, including sources and figures.
        * Error conditions.

---

**Summary of Separation:**

* **Main Python Script (Core Logic - e.g., `claude_core.py`):**
    * Handles backend processing, API interactions, business logic, generation of textual results, and paths/URLs to any figures.
    * UI-agnostic (returns data).
    * Contains the refactored `ClaudeWithCodeExecution` class.

* **Teams Bot & UI/UX Files (New Files - e.g., `bot.py`, `teams_formatter.py`):**
    * **`bot.py`:** Handles Teams events, conversation flow, file downloads from Teams, calls core logic, passes data to formatter. Manages accessibility of figures for the formatter.
    * **`teams_formatter.py`:** Takes structured data (including figure paths/URLs and source details) from the core logic and formats it specifically for Teams (plain text messages, Adaptive Card JSON, or HTML content for Tabs), styled according to the template.