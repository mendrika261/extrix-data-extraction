from .parser import parse_args
from .commands import execute_extraction
import sys

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    
    try:
        parsed_args = parse_args(args)
        return execute_extraction(parsed_args)
    except Exception as e:
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        console.print(Panel(
            f"[bold red]Error:[/bold red] {str(e)}",
            title="[bold red]Error occurred[/bold red]",
            border_style="red"
        ))
        return 1
