#!/usr/bin/env python3
"""
Teams UI/UX Formatter Module
Formats responses from claude_core for display in Microsoft Teams using Adaptive Cards
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from botbuilder.schema import Attachment
from botbuilder.core import CardFactory


class TeamsFormatter:
    """Formats claude_core responses for Teams display"""
    
    def __init__(self):
        """Initialize the formatter with default settings"""
        self.company_name = "TC TASMAN CONSULTING ENGINEERS"
        self.company_tagline = "CIVIL & STRUCTURAL"
        self.company_address = "192a Queen St\nPO Box 3631\nRichmond NELSON"
        self.company_phone = "t: (03) 544 6454"
        self.company_web = "w: www.tcel.co.nz"
    
    def create_detailed_report_card(self, response_data: Dict[str, Any], 
                                    job_details: Dict[str, str]) -> Attachment:
        """
        Create a detailed report card styled after the TCEL template
        
        Args:
            response_data: Response from claude_core.chat()
            job_details: Dictionary with job/project details
            
        Returns:
            Adaptive Card attachment
        """
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Build the card body
        card_body = []
        
        # Header Section with company branding
        header_columns = [
            {
                "type": "Column",
                "width": "auto",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "TC",
                        "size": "Large",
                        "weight": "Bolder",
                        "color": "Accent",
                        "spacing": "None"
                    },
                    {
                        "type": "TextBlock",
                        "text": "E",
                        "size": "Large",
                        "weight": "Bolder",
                        "color": "Good",
                        "spacing": "None"
                    }
                ]
            },
            {
                "type": "Column",
                "width": "stretch",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": self.company_name,
                        "weight": "Bolder",
                        "size": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": self.company_tagline,
                        "size": "Small",
                        "isSubtle": True
                    }
                ]
            },
            {
                "type": "Column",
                "width": "auto",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": self.company_address,
                        "size": "Small",
                        "wrap": True,
                        "horizontalAlignment": "Right"
                    },
                    {
                        "type": "TextBlock",
                        "text": f"{self.company_phone}\n{self.company_web}",
                        "size": "Small",
                        "isSubtle": True,
                        "horizontalAlignment": "Right"
                    }
                ]
            }
        ]
        
        card_body.append({
            "type": "ColumnSet",
            "columns": header_columns,
            "separator": True
        })
        
        # Job Details Section
        job_facts = []
        if job_details.get('project'):
            job_facts.append({"title": "Project:", "value": job_details['project']})
        if job_details.get('description'):
            job_facts.append({"title": "Description:", "value": job_details['description']})
        if job_details.get('client'):
            job_facts.append({"title": "Client:", "value": job_details['client']})
        if job_details.get('job_reference'):
            job_facts.append({"title": "Job Reference:", "value": job_details['job_reference']})
        job_facts.append({"title": "Date:", "value": current_date})
        if job_details.get('by'):
            job_facts.append({"title": "By:", "value": job_details['by']})
        
        card_body.append({
            "type": "FactSet",
            "facts": job_facts,
            "separator": True,
            "spacing": "Medium"
        })
        
        # Main Content Section
        card_body.append({
            "type": "TextBlock",
            "text": "Analysis Results",
            "size": "Large",
            "weight": "Bolder",
            "spacing": "Large"
        })
        
        # Assistant's Summary
        if response_data.get('assistant_message'):
            # Extract just the text part (remove code blocks from message)
            summary = response_data['assistant_message']
            if '[Executed code:' in summary:
                summary = summary.split('[Executed code:')[0].strip()
            
            card_body.append({
                "type": "TextBlock",
                "text": summary,
                "wrap": True,
                "spacing": "Medium"
            })
        
        # Code Execution Section
        if response_data.get('executed_code'):
            card_body.append({
                "type": "TextBlock",
                "text": "📝 Executed Code",
                "weight": "Bolder",
                "size": "Medium",
                "spacing": "Large"
            })
            
            card_body.append({
                "type": "TextBlock",
                "text": response_data['executed_code'],
                "fontType": "Monospace",
                "wrap": True,
                "size": "Small"
            })
        
        # Code Output Section
        if response_data.get('code_output'):
            card_body.append({
                "type": "TextBlock",
                "text": "💻 Output",
                "weight": "Bolder",
                "size": "Medium",
                "spacing": "Large"
            })
            
            card_body.append({
                "type": "TextBlock",
                "text": response_data['code_output'],
                "fontType": "Monospace",
                "wrap": True,
                "size": "Small"
            })
        
        # Generated Figures Section
        if response_data.get('generated_figures'):
            card_body.append({
                "type": "TextBlock",
                "text": "📊 Generated Figures",
                "weight": "Bolder",
                "size": "Medium",
                "spacing": "Large"
            })
            
            for figure in response_data['generated_figures']:
                card_body.append({
                    "type": "TextBlock",
                    "text": f"• {figure['figure_name']}",
                    "wrap": True
                })
                # In production, you'd include actual Image elements with URLs
                # card_body.append({
                #     "type": "Image",
                #     "url": figure['path_or_url'],
                #     "size": "Large"
                # })
        
        # Errors Section
        if response_data.get('code_errors'):
            card_body.append({
                "type": "Container",
                "style": "attention",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "❌ Errors",
                        "weight": "Bolder",
                        "size": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": response_data['code_errors'],
                        "fontType": "Monospace",
                        "wrap": True,
                        "size": "Small"
                    }
                ],
                "spacing": "Large"
            })
        
        # Sources Section
        if response_data.get('web_searches'):
            card_body.append({
                "type": "TextBlock",
                "text": "🌐 Sources",
                "weight": "Bolder",
                "size": "Medium",
                "spacing": "Large",
                "separator": True
            })
            
            for search in response_data['web_searches']:
                for idx, result in enumerate(search.get('results', [])[:5]):  # Limit to 5 sources
                    source_text = f"{idx + 1}. [{result['title']}]({result['url']})"
                    if result.get('published') and result['published'] != 'N/A':
                        source_text += f" - {result['published']}"
                    
                    card_body.append({
                        "type": "TextBlock",
                        "text": source_text,
                        "wrap": True,
                        "size": "Small"
                    })
        
        # Create the Adaptive Card
        card = {
            "type": "AdaptiveCard",
            "version": "1.3",
            "body": card_body,
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }
        
        return CardFactory.adaptive_card(card)
    
    def create_simple_text_card(self, text: str) -> Attachment:
        """Create a simple text response card"""
        card = {
            "type": "AdaptiveCard",
            "version": "1.3",
            "body": [
                {
                    "type": "TextBlock",
                    "text": text,
                    "wrap": True
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }
        return CardFactory.adaptive_card(card)
    
    def create_files_list_card(self, files: List[Dict[str, Any]]) -> Attachment:
        """Create a card showing uploaded files"""
        card_body = [
            {
                "type": "TextBlock",
                "text": "📁 Uploaded Files",
                "size": "Large",
                "weight": "Bolder"
            }
        ]
        
        # Create a table-like structure
        for file in files:
            file_container = {
                "type": "Container",
                "items": [
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {
                                "type": "Column",
                                "width": "stretch",
                                "items": [{
                                    "type": "TextBlock",
                                    "text": file['file_name'],
                                    "weight": "Bolder"
                                }]
                            },
                            {
                                "type": "Column",
                                "width": "auto",
                                "items": [{
                                    "type": "TextBlock",
                                    "text": file['file_type'],
                                    "color": "Accent"
                                }]
                            }
                        ]
                    },
                    {
                        "type": "TextBlock",
                        "text": f"ID: {file['file_id']}",
                        "size": "Small",
                        "isSubtle": True
                    }
                ],
                "separator": True
            }
            card_body.append(file_container)
        
        card = {
            "type": "AdaptiveCard",
            "version": "1.3",
            "body": card_body,
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }
        
        return CardFactory.adaptive_card(card)
    
    def create_help_card(self) -> Attachment:
        """Create a help card with available commands"""
        card = {
            "type": "AdaptiveCard",
            "version": "1.3",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "📚 Claude Code Execution Assistant - Help",
                    "size": "Large",
                    "weight": "Bolder"
                },
                {
                    "type": "TextBlock",
                    "text": "Available Commands:",
                    "weight": "Bolder",
                    "spacing": "Medium"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "/help", "value": "Show this help message"},
                        {"title": "/reset", "value": "Clear conversation history"},
                        {"title": "/files", "value": "List uploaded files"},
                        {"title": "/nocode <message>", "value": "Send message without code execution"}
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": "Features:",
                    "weight": "Bolder",
                    "spacing": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": "• 🐍 **Python Code Execution** - I can write and execute Python code\n• 📊 **Data Analysis** - Process data and generate visualizations\n• 🌐 **Web Search** - Access current information from the web\n• 📎 **File Support** - Upload files for analysis\n• 📈 **Report Generation** - Formatted reports with results",
                    "wrap": True
                },
                {
                    "type": "TextBlock",
                    "text": "Simply send me a message with your request, and I'll help you analyze data, write code, or answer questions!",
                    "wrap": True,
                    "spacing": "Medium"
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Try an Example",
                    "data": {
                        "text": "Create a simple bar chart showing sales data for Q1-Q4"
                    }
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }
        
        return CardFactory.adaptive_card(card)
    
    def create_welcome_card(self) -> Attachment:
        """Create a welcome card for new users"""
        card = {
            "type": "AdaptiveCard",
            "version": "1.3",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "🤖 Welcome to Claude Code Execution Assistant!",
                    "size": "Large",
                    "weight": "Bolder"
                },
                {
                    "type": "TextBlock",
                    "text": "I'm Claude, your AI assistant with advanced code execution capabilities. I can help you with:",
                    "wrap": True,
                    "spacing": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": "✨ **Data Analysis** - Process and visualize your data\n🐍 **Python Programming** - Write and execute code\n📊 **Report Generation** - Create formatted analysis reports\n🔍 **Research** - Search the web for current information",
                    "wrap": True
                },
                {
                    "type": "TextBlock",
                    "text": "Type **/help** to see available commands, or just start chatting!",
                    "wrap": True,
                    "spacing": "Medium"
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Get Started",
                    "data": {
                        "text": "/help"
                    }
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }
        
        return CardFactory.adaptive_card(card)
    
    def create_error_card(self, error_message: str) -> Attachment:
        """Create an error notification card"""
        card = {
            "type": "AdaptiveCard",
            "version": "1.3",
            "body": [
                {
                    "type": "Container",
                    "style": "attention",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "auto",
                                    "items": [{
                                        "type": "TextBlock",
                                        "text": "❌",
                                        "size": "Large"
                                    }]
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "An Error Occurred",
                                            "weight": "Bolder"
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": error_message,
                                            "wrap": True
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
        }
        
        return CardFactory.adaptive_card(card)