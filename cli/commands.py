from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from .processor import CliProcessor
from .ui import CONSOLE as console, display_summary, print_banner
from core.utils import find_files
from core.exceptions import OSNotSupportedError

def execute_extraction(args) -> int:
    try:
        print_banner()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(complete_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            refresh_per_second=1,
            expand=True,
            console=console
        ) as progress:
            processor = CliProcessor(args)
            
            files = find_files(args.input_pattern)
            if not files:
                console.print(f"[bold red]No files found matching pattern:[/bold red] {args.input_pattern}")
                return 1
            
            results = processor.process_files(files, progress)
            
            display_summary(*results)
            
            return 0 if results[0] > 0 else 1

    except OSNotSupportedError as e:
        console.print(f"[bold red]OS Compatibility Error:[/bold red] {str(e)}")
        return 1