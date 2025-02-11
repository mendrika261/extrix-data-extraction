from typing import List
from rich.console import Console
from rich.panel import Panel
from .models import ProcessingError

VERSION = "0.1-beta"
CONSOLE = Console()

def print_banner():
    CONSOLE.print(Panel.fit(
        "[bold blue]Extrix - Document Information Extractor[/bold blue]\n"
        f"[cyan]CLI Version {VERSION}[/cyan]",
        border_style="bright_blue",
        padding=(1, 2)
    ))

def display_summary(successful: int, errors: List[ProcessingError]) -> None:
    CONSOLE.print("\n[bold green]Processing complete![/bold green]")
    CONSOLE.print(f"Successfully processed: {successful} file(s)")
    
    if errors:
        CONSOLE.print("\n[bold red]Failed files:[/bold red]")
        for error in errors:
            CONSOLE.print(f"[red]• {error.file}:[/red] {error.reason}")
    CONSOLE.print("\n")
