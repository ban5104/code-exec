#!/usr/bin/env python3
"""AI Terminal Visualizer - Real-time visualization of AI interactions."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.app import TerminalApp
from src.utils.config import Config, load_config


# Load environment variables
load_dotenv()

# Create global console instance (singleton)
console = Console()


@click.command()
@click.option(
    "--model",
    "-m",
    default="claude-3-5-sonnet-20241022",
    help="AI model to use",
    type=click.Choice([
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
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration file"
)
@click.option(
    "--theme",
    "-t",
    default="monokai",
    help="Color theme for syntax highlighting",
    type=click.Choice(["monokai", "dracula", "solarized", "github"])
)
@click.option(
    "--timeout",
    default=30,
    help="Code execution timeout in seconds",
    type=int
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode with verbose logging"
)
def main(
    model: str,
    api_key: Optional[str],
    config: Optional[str],
    theme: str,
    timeout: int,
    debug: bool
):
    """AI Terminal Visualizer - Watch AI think and code in real-time.
    
    This tool provides transparent visualization of AI model interactions,
    showing code generation and execution as it happens.
    """
    
    # Check for API key
    if not api_key:
        console.print(
            "[red]Error:[/red] No API key provided. "
            "Set ANTHROPIC_API_KEY environment variable or use --api-key option."
        )
        sys.exit(1)
    
    # Load configuration
    if config:
        app_config = load_config(Path(config))
    else:
        app_config = Config(
            model=model,
            api_key=api_key,
            theme=theme,
            execution_timeout=timeout,
            debug=debug
        )
    
    # Override config with command line options
    app_config.model = model
    app_config.api_key = api_key
    app_config.theme = theme
    app_config.execution_timeout = timeout
    app_config.debug = debug
    
    # Print welcome message
    console.print(
        "\n[bold cyan]AI Terminal Visualizer v1.0[/bold cyan]\n"
        f"Model: [green]{model}[/green]\n"
        f"Theme: [yellow]{theme}[/yellow]\n"
    )
    
    # Create and run the app
    app = TerminalApp(config=app_config, console=console)
    
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Fatal error:[/red] {str(e)}")
        if debug:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()