from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)

from core.service import extract_from_config_file

from cli.ui import CONSOLE as console, display_summary, print_banner
from core.utils import find_files
from core.exceptions import OSNotSupportedError


def execute_extraction(args) -> None:
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
            console=console,
        ) as progress:
            files = find_files(args.files_path)
            if not files:
                console.print(
                    f"[bold red]No files found matching pattern:[/bold red] {args.files_path}"
                )

            args_dict = vars(args)
            args_dict.pop("files_path")

            results = extract_from_config_file(
                **args_dict,
                files_path=files,
                progress=progress,
            )
            display_summary(*results, args.output)

    except OSNotSupportedError as e:
        console.print(f"[bold red]OS Compatibility Error:[/bold red] {str(e)}")
