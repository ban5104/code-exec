#!/usr/bin/env python3
"""
Claude with Code Execution Tool
This script provides an interactive Claude assistant with code execution capabilities.
"""

import os
import sys
from anthropic import Anthropic
from typing import Optional
import json
import readline
import click
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Prompt
import sys

class ClaudeWithCodeExecution:
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-opus-4-20250514", theme: str = "monokai", console: Optional[Console] = None):
        """Initialize Claude client with code execution tool support."""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it as an environment variable or pass it to the constructor.")
        
        self.client = Anthropic(
            api_key=self.api_key,
            default_headers={
                "anthropic-beta": "code-execution-2025-05-22,files-api-2025-04-14"
            }
        )
        
        self.conversation_history = []
        self.model = model
        self.theme = theme
        self.console = console or Console()
        self.uploaded_files = {}  # Store file IDs and their info
        self.web_searches = []  # Track web search queries and results
        self.files_accessed = []  # Track files accessed during conversations
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})
    
    def get_file_type(self, file_path: str) -> str:
        """Determine file type based on extension."""
        ext = os.path.splitext(file_path)[1].lower()
        file_type_map = {
            '.pdf': 'PDF Document',
            '.txt': 'Text Document', 
            '.xlsx': 'Excel Spreadsheet',
            '.xls': 'Excel Spreadsheet',
            '.csv': 'CSV Data',
            '.json': 'JSON Data',
            '.png': 'Image',
            '.jpg': 'Image',
            '.jpeg': 'Image'
        }
        return file_type_map.get(ext, 'Unknown')

    def upload_file(self, file_path: str):
        """Upload a file using the Files API."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Uploading {os.path.basename(file_path)}...", total=None)
                
                with open(file_path, 'rb') as file:
                    file_upload = self.client.files.create(
                        file=file,
                        purpose="user_request"
                    )
                
                progress.update(task, completed=True)
                
                file_name = os.path.basename(file_path)
                file_type = self.get_file_type(file_path)
                self.uploaded_files[file_name] = {
                    'file_id': file_upload.id,
                    'file_path': file_path,
                    'file_type': file_type
                }
                self.console.print(f"[green]✅ Uploaded file:[/green] {file_name} [blue]({file_type})[/blue] [dim](ID: {file_upload.id})[/dim]")
                return file_upload.id
        except Exception as e:
            self.console.print(f"[red]❌ Error uploading file {file_path}:[/red] {e}")
            return None
    
    def list_files(self):
        """List all uploaded files."""
        if not self.uploaded_files:
            self.console.print("[yellow]No files uploaded yet.[/yellow]")
            return
            
        table = Table(title="📁 Uploaded Files", show_header=True, header_style="bold magenta")
        table.add_column("File Name", style="cyan")
        table.add_column("Type", style="blue")
        table.add_column("File ID", style="dim")
        table.add_column("Path", style="green")
        
        for file_name, info in self.uploaded_files.items():
            table.add_row(file_name, info.get('file_type', 'Unknown'), info['file_id'], info['file_path'])
        
        self.console.print(table)
    
    def track_web_search(self, query: str, results: list = None):
        """Track a web search query and its results."""
        import datetime
        search_entry = {
            'query': query,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': results or []
        }
        self.web_searches.append(search_entry)
    
    def list_web_searches(self):
        """Display web search history in a table."""
        if not self.web_searches:
            self.console.print("[yellow]No web searches performed yet.[/yellow]")
            return
        
        # Show search queries table
        search_table = Table(title="🔍 Web Search History", show_header=True, header_style="bold cyan")
        search_table.add_column("#", style="dim", width=3)
        search_table.add_column("Query", style="green")
        search_table.add_column("Timestamp", style="blue")
        search_table.add_column("Results Count", style="yellow")
        
        for i, search in enumerate(self.web_searches, 1):
            search_table.add_row(
                str(i), 
                search['query'], 
                search['timestamp'],
                str(len(search['results']))
            )
        
        self.console.print(search_table)
        
        # Show latest search results if available
        if self.web_searches and self.web_searches[-1]['results']:
            latest_search = self.web_searches[-1]
            results_table = Table(title=f"🌐 WEB SEARCH RESULTS - Found {len(latest_search['results'])} sources", 
                                show_header=True, header_style="bold red")
            results_table.add_column("#", style="dim", width=3)
            results_table.add_column("Title", style="cyan", max_width=50)
            results_table.add_column("URL", style="blue", max_width=40)
            results_table.add_column("Published", style="yellow")
            
            for i, result in enumerate(latest_search['results'][:10], 1):  # Show top 10 results
                results_table.add_row(
                    str(i),
                    result.get('title', 'N/A')[:47] + ('...' if len(result.get('title', '')) > 47 else ''),
                    result.get('url', 'N/A')[:37] + ('...' if len(result.get('url', '')) > 37 else ''),
                    result.get('published', 'N/A')
                )
            
            self.console.print(results_table)
    
    def track_file_access(self, file_name: str, action: str = "accessed"):
        """Track when a file is accessed or used."""
        import datetime
        access_entry = {
            'file_name': file_name,
            'action': action,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.files_accessed.append(access_entry)
    
    def list_file_usage(self):
        """Display file usage history in a table."""
        if not self.files_accessed:
            self.console.print("[yellow]No file access history yet.[/yellow]")
            return
            
        table = Table(title="📊 File Usage History", show_header=True, header_style="bold green")
        table.add_column("#", style="dim", width=3)
        table.add_column("File Name", style="cyan")
        table.add_column("Action", style="yellow")
        table.add_column("Timestamp", style="blue")
        
        for i, access in enumerate(self.files_accessed, 1):
            table.add_row(
                str(i),
                access['file_name'],
                access['action'],
                access['timestamp']
            )
        
        self.console.print(table)
    
    def delete_file(self, file_name: str):
        """Delete an uploaded file."""
        if file_name not in self.uploaded_files:
            self.console.print(f"[red]❌ File '{file_name}' not found in uploaded files.[/red]")
            return False
            
        try:
            file_id = self.uploaded_files[file_name]['file_id']
            self.client.files.delete(file_id)
            del self.uploaded_files[file_name]
            self.console.print(f"[green]✅ Deleted file:[/green] {file_name}")
            return True
        except Exception as e:
            self.console.print(f"[red]❌ Error deleting file {file_name}:[/red] {e}")
            return False
    
    def chat(self, user_input: str, use_code_execution: bool = True, file_attachments: list = None):
        """Send a message to Claude and get a response with streaming."""
        # Prepare message content
        message_content = [{"type": "text", "text": user_input}]
        
        # Add file attachments if provided
        if file_attachments:
            for file_info in file_attachments:
                message_content.append({
                    "type": "file", 
                    "file": {"file_id": file_info['file_id']}
                })
                # Track file access
                file_name = file_info.get('file_name', file_info.get('file_id', 'Unknown file'))
                self.track_file_access(file_name, "attached to message")
        
        self.conversation_history.append({"role": "user", "content": message_content})
        
        # Prepare tools based on user preference
        tools = []
        if use_code_execution:
            tools.append({
                "type": "code_execution_20250522",
                "name": "code_execution"
            })
        
        try:
            # Use streaming
            stream = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=self.conversation_history,
                tools=tools if tools else None,
                stream=True
            )
            
            # Process the streaming response
            assistant_message = ""
            current_tool_input = ""
            in_code_block = False
            web_search_detected = False
            current_search_query = ""
            
            for event in stream:
                # Debug: Uncomment to see event types
                # print(f"\nDEBUG: Event type: {event.type}", flush=True)
                # if hasattr(event, 'delta'):
                #     print(f"DEBUG: Delta: {event.delta}", flush=True)
                
                if event.type == "message_start":
                    continue
                elif event.type == "content_block_start":
                    if hasattr(event, 'content_block'):
                        if event.content_block.type == "server_tool_use" and event.content_block.name == "code_execution":
                            in_code_block = True
                            self.console.print("\n[bold blue]📝 Executing Python code:[/bold blue]")
                            self.console.print("```python", end="", style="dim")
                        elif hasattr(event.content_block, 'name') and 'search' in event.content_block.name.lower():
                            # Track web search usage
                            web_search_detected = True
                            self.console.print("\n[bold yellow]🔍 Web search detected[/bold yellow]")
                elif event.type == "content_block_delta":
                    if hasattr(event, 'delta'):
                        if hasattr(event.delta, 'text'):
                            # Regular text
                            self.console.print(event.delta.text, end="")
                            assistant_message += event.delta.text
                        elif hasattr(event.delta, 'partial_json'):
                            # Tool use with partial JSON
                            if in_code_block and event.delta.partial_json:
                                try:
                                    # For complete JSON
                                    if event.delta.partial_json.startswith('{') and event.delta.partial_json.endswith('}'):
                                        partial = json.loads(event.delta.partial_json)
                                        if 'code' in partial:
                                            code_chunk = partial['code'][len(current_tool_input):]
                                            self.console.print(code_chunk, end="", style="cyan")
                                            current_tool_input = partial['code']
                                    else:
                                        # For partial chunks, extract the new part
                                        if '"code": "' in event.delta.partial_json:
                                            # First chunk with code
                                            start = event.delta.partial_json.find('"code": "') + 9
                                            code_part = event.delta.partial_json[start:]
                                            # Remove any trailing quote or brace
                                            code_part = code_part.rstrip('"}')
                                            # Decode escape sequences
                                            code_part = code_part.encode('utf-8').decode('unicode_escape')
                                            self.console.print(code_part, end="", style="cyan")
                                            current_tool_input += code_part
                                        elif event.delta.partial_json not in ['', '{"code": "', '"}']:
                                            # Subsequent chunks
                                            code_part = event.delta.partial_json.rstrip('"}')
                                            # Decode escape sequences
                                            code_part = code_part.encode('utf-8').decode('unicode_escape')
                                            self.console.print(code_part, end="", style="cyan")
                                            current_tool_input += code_part
                                except Exception as e:
                                    # Debug
                                    # print(f"\nDEBUG: Error parsing: {e}", flush=True)
                                    pass
                            elif web_search_detected and event.delta.partial_json:
                                # Try to extract search query from web search tool
                                try:
                                    if '"query"' in event.delta.partial_json:
                                        # Extract query for tracking
                                        import re
                                        query_match = re.search(r'"query"\s*:\s*"([^"]+)"', event.delta.partial_json)
                                        if query_match:
                                            current_search_query = query_match.group(1)
                                except:
                                    pass
                elif event.type == "content_block_stop":
                    if in_code_block:
                        self.console.print("\n```", style="dim")
                        in_code_block = False
                        assistant_message += f"\n\n[Executed code:\n```python\n{current_tool_input}\n```]"
                        current_tool_input = ""
                elif event.type == "server_tool_result":
                    # Handle server tool results
                    if hasattr(event, 'result'):
                        if web_search_detected:
                            # Handle web search results
                            try:
                                if hasattr(event.result, 'content') and event.result.content:
                                    result_text = event.result.content
                                    # Try to parse search results
                                    search_results = self.parse_search_results(result_text)
                                    if current_search_query:
                                        self.track_web_search(current_search_query, search_results)
                                        self.console.print(f"\n[bold green]🌐 Web search completed:[/bold green] {len(search_results)} results found")
                                        current_search_query = ""
                                    web_search_detected = False
                            except:
                                pass
                        else:
                            # Handle code execution results
                            self.console.print("\n[bold green]💻 Code Output:[/bold green]")
                            if hasattr(event.result, 'stdout'):
                                if event.result.stdout:
                                    # Use syntax highlighting for output
                                    syntax = Syntax(event.result.stdout, "text", theme=self.theme, line_numbers=False)
                                    self.console.print(Panel(syntax, border_style="green"))
                                    assistant_message += f"\n[Code Output]:\n{event.result.stdout}"
                            if hasattr(event.result, 'stderr') and event.result.stderr:
                                self.console.print(f"[bold red]❌ Errors:[/bold red]")
                                syntax = Syntax(event.result.stderr, "text", theme=self.theme, line_numbers=False)
                                self.console.print(Panel(syntax, border_style="red"))
                                assistant_message += f"\n[Errors]:\n{event.result.stderr}"
                elif event.type == "message_delta":
                    if hasattr(event, 'delta') and hasattr(event.delta, 'stop_reason'):
                        # Message is complete
                        pass
                elif event.type == "message_stop":
                    # Final message complete
                    pass
            
            self.add_message("assistant", assistant_message)
            return assistant_message
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def parse_search_results(self, result_text: str) -> list:
        """Parse web search results from tool output."""
        results = []
        try:
            # Try to parse as JSON first
            if result_text.strip().startswith('{') or result_text.strip().startswith('['):
                import json
                data = json.loads(result_text)
                
                # Handle different JSON structures
                if isinstance(data, dict):
                    if 'results' in data:
                        search_results = data['results']
                    elif 'web' in data and 'results' in data['web']:
                        search_results = data['web']['results']
                    else:
                        search_results = [data]
                else:
                    search_results = data
                
                # Extract title, URL, and date from each result
                for item in search_results[:10]:  # Limit to 10 results
                    result_item = {
                        'title': item.get('title', item.get('name', 'N/A')),
                        'url': item.get('url', item.get('link', 'N/A')),
                        'published': item.get('published', item.get('date', item.get('timestamp', 'N/A')))
                    }
                    results.append(result_item)
            else:
                # Fallback: create a simple result entry
                results.append({
                    'title': 'Search completed',
                    'url': 'N/A',
                    'published': 'N/A'
                })
        except:
            # If parsing fails, create a generic entry
            results.append({
                'title': 'Search completed',
                'url': 'N/A', 
                'published': 'N/A'
            })
        
        return results
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        self.console.print("[yellow]Conversation history cleared.[/yellow]")
    
    def set_model(self, model: str):
        """Change the model being used."""
        self.model = model
        self.console.print(f"[green]Model changed to:[/green] [bold]{model}[/bold]")
    
    def get_files_by_type(self, file_type: str) -> list:
        """Get all uploaded files of a specific type."""
        return [info for name, info in self.uploaded_files.items() 
                if info.get('file_type', '').lower().find(file_type.lower()) != -1]
    
    def attach_all_files_of_type(self, file_type: str) -> list:
        """Get file attachments for all files of a specific type."""
        matching_files = self.get_files_by_type(file_type)
        return [{'file_id': info['file_id'], 'file_name': name} 
                for name, info in self.uploaded_files.items() 
                if info in matching_files]
    
    def import_existing_file(self, file_id: str, filename: str, file_type: str = None):
        """Import an already uploaded file by its ID."""
        if not file_type:
            file_type = self.get_file_type(filename)
        
        self.uploaded_files[filename] = {
            'file_id': file_id,
            'file_path': f'[Already uploaded] {filename}',
            'file_type': file_type
        }
        self.console.print(f"[green]✅ Imported existing file:[/green] {filename} [blue]({file_type})[/blue] [dim](ID: {file_id})[/dim]")
        return file_id
    
    def list_api_files(self):
        """List all files in your Anthropic account."""
        try:
            # Use the beta files API endpoint directly
            import requests
            
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "anthropic-beta": "files-api-2025-04-14"
            }
            
            response = requests.get("https://api.anthropic.com/v1/files", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('data'):
                self.console.print("[yellow]No files found in your Anthropic account.[/yellow]")
                return
            
            table = Table(title="🌐 Files in Your Anthropic Account", show_header=True, header_style="bold cyan")
            table.add_column("Filename", style="green")
            table.add_column("File ID", style="dim")
            table.add_column("Size", style="blue")
            table.add_column("Created", style="yellow")
            
            for file in data['data']:
                size_mb = round(file['size_bytes'] / 1024 / 1024, 2)
                created = file['created_at'].split('T')[0]  # Just the date part
                table.add_row(file['filename'], file['id'], f"{size_mb} MB", created)
            
            self.console.print(table)
            self.console.print("\n[cyan]💡 Use /import <file_id> <filename> to import existing files[/cyan]")
            self.console.print("[cyan]💡 Use /attachid <file_id> to attach directly to next message[/cyan]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Error listing API files:[/red] {e}")
            self.console.print("[yellow]💡 Make sure ANTHROPIC_API_KEY is set correctly[/yellow]")

def show_help(console: Console):
    """Display help information."""
    help_panel = Panel(
        """[bold cyan]Available Commands:[/bold cyan]

[yellow]/quit or /exit[/yellow] - Exit the program
[yellow]/reset[/yellow] - Clear conversation history  
[yellow]/model <name>[/yellow] - Change the model
[yellow]/nocode[/yellow] - Send next message without code execution
[yellow]/upload <path>[/yellow] - Upload a new file
[yellow]/files[/yellow] - List imported files
[yellow]/listapi[/yellow] - List ALL files in your Anthropic account
[yellow]/import <id> <name>[/yellow] - Import existing file by ID
[yellow]/attachid <file_id>[/yellow] - Attach file by ID to next message
[yellow]/attach <name>[/yellow] - Attach imported file to next message
[yellow]/delete <name>[/yellow] - Delete an imported file
[yellow]/multiline[/yellow] - Switch to multi-line input mode
[yellow]/paste[/yellow] - Paste from clipboard (if available)
[yellow]/searches[/yellow] - Show web search history and latest results
[yellow]/fileusage[/yellow] - Show file access history
[yellow]/help[/yellow] - Show this help message
        """,
        title="📚 Help",
        border_style="blue"
    )
    console.print(help_panel)

def get_multiline_input(console: Console) -> str:
    """Get multi-line input that supports pasting and Ctrl+D to finish."""
    console.print("\n[bold blue]👤 You[/bold blue] (paste your text, then press Ctrl+D on a new line to finish):")
    console.print("[dim]Or just type normally and press Enter for single line input[/dim]")
    
    lines = []
    try:
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                # Ctrl+D pressed
                break
    except KeyboardInterrupt:
        # Ctrl+C pressed
        raise
    
    return '\n'.join(lines).strip()

def get_input(console: Console) -> str:
    """Get input with support for both single-line and multi-line."""
    try:
        # Try single line input first
        console.print("\n[bold blue]👤 You[/bold blue] ", end="")
        
        # Configure readline for better paste support
        readline.parse_and_bind("set enable-bracketed-paste on")
        
        user_input = input().strip()
        
        # Check for special commands
        if user_input.lower() == '/multiline':
            return get_multiline_input(console)
        elif user_input.lower() == '/paste' and CLIPBOARD_AVAILABLE:
            try:
                clipboard_content = pyperclip.paste()
                if clipboard_content:
                    console.print(f"[green]📋 Pasted {len(clipboard_content)} characters from clipboard[/green]")
                    return clipboard_content
                else:
                    console.print("[yellow]📋 Clipboard is empty[/yellow]")
                    return get_input(console)
            except Exception as e:
                console.print(f"[red]❌ Error accessing clipboard: {e}[/red]")
                return get_input(console)
        
        return user_input
        
    except KeyboardInterrupt:
        raise
    except EOFError:
        # If EOF on first line, user probably pasted multi-line content
        # Let's try to get the rest
        return get_multiline_input(console)

def interactive_loop(claude: ClaudeWithCodeExecution):
    """Main interactive loop."""
    console = claude.console
    use_code_execution = True
    pending_file_attachments = []
    
    # Print input instructions
    console.print("\n[cyan]💡 Input Options:[/cyan]")
    console.print("  • [yellow]Single line:[/yellow] Just type and press Enter")
    console.print("  • [yellow]Multi-line:[/yellow] Type /multiline then paste content and press Ctrl+D")
    console.print("  • [yellow]Paste directly:[/yellow] Paste multi-line content and press Ctrl+D")
    if CLIPBOARD_AVAILABLE:
        console.print("  • [yellow]Clipboard:[/yellow] Type /paste to paste from clipboard")
    console.print("  • [yellow]Most terminals:[/yellow] Right-click to paste or Ctrl+Shift+V\n")
    
    while True:
        try:
            user_input = get_input(console)
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['/quit', '/exit']:
                console.print("[yellow]👋 Goodbye![/yellow]")
                break
            elif user_input.lower() == '/reset':
                claude.reset_conversation()
                continue
            elif user_input.lower().startswith('/model '):
                model_name = user_input[7:].strip()
                claude.set_model(model_name)
                continue
            elif user_input.lower() == '/nocode':
                use_code_execution = False
                console.print("[yellow]📝 Code execution disabled for next message[/yellow]")
                continue
            elif user_input.lower().startswith('/upload '):
                file_path = user_input[8:].strip()
                claude.upload_file(file_path)
                continue
            elif user_input.lower() == '/files':
                claude.list_files()
                continue
            elif user_input.lower().startswith('/delete '):
                file_name = user_input[8:].strip()
                claude.delete_file(file_name)
                continue
            elif user_input.lower().startswith('/attach '):
                file_name = user_input[8:].strip()
                if file_name in claude.uploaded_files:
                    pending_file_attachments.append(claude.uploaded_files[file_name])
                    console.print(f"[green]📎 File '{file_name}' will be attached to your next message[/green]")
                else:
                    console.print(f"[red]❌ File '{file_name}' not found. Use /files to see uploaded files.[/red]")
                continue
            elif user_input.lower() == '/help':
                show_help(console)
                continue
            elif user_input.lower() == '/listapi':
                claude.list_api_files()
                continue
            elif user_input.lower().startswith('/import '):
                parts = user_input[8:].strip().split(' ', 1)
                if len(parts) >= 2:
                    file_id, filename = parts[0], parts[1]
                    claude.import_existing_file(file_id, filename)
                else:
                    console.print("[red]❌ Usage: /import <file_id> <filename>[/red]")
                continue
            elif user_input.lower().startswith('/attachid '):
                file_id = user_input[10:].strip()
                # Find the file in API files and attach it
                try:
                    import requests
                    
                    headers = {
                        "x-api-key": claude.api_key,
                        "anthropic-version": "2023-06-01",
                        "anthropic-beta": "files-api-2025-04-14"
                    }
                    
                    response = requests.get("https://api.anthropic.com/v1/files", headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    found_file = None
                    for file in data.get('data', []):
                        if file['id'] == file_id:
                            found_file = file
                            break
                    
                    if found_file:
                        # Import it temporarily and attach
                        claude.import_existing_file(file_id, found_file['filename'])
                        pending_file_attachments.append({'file_id': file_id, 'file_name': found_file['filename']})
                        console.print(f"[green]📎 File '{found_file['filename']}' will be attached to your next message[/green]")
                    else:
                        console.print(f"[red]❌ File ID '{file_id}' not found in your account[/red]")
                        console.print("[yellow]💡 Use /listapi to see available files[/yellow]")
                except Exception as e:
                    console.print(f"[red]❌ Error finding file: {e}[/red]")
                continue
            elif user_input.lower() == '/searches':
                claude.list_web_searches()
                continue
            elif user_input.lower() == '/fileusage':
                claude.list_file_usage()
                continue
            
            # Send message to Claude
            console.print("\n[bold green]🤖 Claude:[/bold green] ", end="")
            response = claude.chat(user_input, use_code_execution, pending_file_attachments)
            # Response is already printed via streaming, just add newline
            console.print()
            
            # Reset code execution flag and clear file attachments
            if not use_code_execution:
                use_code_execution = True
            pending_file_attachments = []
                
        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]❌ Error: {e}[/red]")

@click.command()
@click.option(
    "--model",
    "-m", 
    default="claude-opus-4-20250514",
    help="AI model to use",
    type=click.Choice([
        "claude-opus-4-20250514",
        "claude-3-5-sonnet-20241022", 
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229"
    ])
)
@click.option(
    "--api-key",
    "-k",
    envvar="ANTHROPIC_API_KEY", 
    help="Anthropic API key (can also use ANTHROPIC_API_KEY env var)"
)
@click.option(
    "--theme",
    "-t",
    default="monokai",
    help="Color theme for syntax highlighting",
    type=click.Choice(["monokai", "dracula", "solarized-dark", "github-dark"])
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode with verbose logging"
)
def main(model: str, api_key: Optional[str], theme: str, debug: bool):
    """Claude with Code Execution Tool - Interactive AI assistant with live code execution.
    
    This tool provides an interactive Claude assistant with advanced code execution capabilities,
    featuring rich terminal UI, file upload support, and real-time code visualization.
    """
    console = Console()
    
    # Print welcome message
    welcome_panel = Panel(
        f"""[bold cyan]Claude with Code Execution Tool v2.0[/bold cyan]

[green]Model:[/green] {model}
[green]Theme:[/green] {theme}
[green]Code Execution:[/green] Enabled
[green]File Upload:[/green] Supported

Type [yellow]/help[/yellow] to see available commands.
        """,
        title="🤖 Welcome",
        border_style="cyan"
    )
    console.print(welcome_panel)
    
    # Check for API key
    if not api_key:
        console.print(
            "[red]Error:[/red] No API key provided. "
            "Set ANTHROPIC_API_KEY environment variable or use --api-key option."
        )
        sys.exit(1)
    
    try:
        claude = ClaudeWithCodeExecution(api_key=api_key, model=model, theme=theme, console=console)
        console.print(f"[green]✅ Connected to Claude[/green] [dim]({model})[/dim]")
        console.print("[blue]💡 Code execution tool is enabled by default[/blue]\n")
        
        interactive_loop(claude)
        
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        if debug:
            console.print_exception()
        sys.exit(1)

if __name__ == "__main__":
    main()