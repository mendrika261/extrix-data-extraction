from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from core.exceptions import ValidationError
from core.models import DataBaseModel

VERSION = "0.1-beta"
CONSOLE = Console()


def print_banner() -> None:
    CONSOLE.print(
        Panel.fit(
            "[bold blue]Extrix - Document Information Extractor[/bold blue]\n"
            f"[cyan]CLI Version {VERSION}[/cyan]",
            border_style="bright_blue",
            padding=(1, 2),
        )
    )


def display_result(result: DataBaseModel) -> None:
    CONSOLE.print(
        Panel(
            Syntax(
                result.model_dump_json(indent=2),
                "json",
                theme="monokai",
                word_wrap=True,
                line_numbers=True,
            ),
            border_style="green",
        )
    )


def display_results(results: list[str | DataBaseModel]) -> None:
    if results:
        CONSOLE.print("\n[bold green]Successful files:[/bold green]")
        for idx, result in enumerate(results, 1):
            if isinstance(result, DataBaseModel):
                display_result(result)
            CONSOLE.print(f"[green]✓ File {idx}[/green]")


def display_error(e: Exception) -> None:
    raise e
    CONSOLE.print(
        Panel(
            f"[bold red]Error:[/bold red] {str(e)}",
            title="[bold red]Error occurred[/bold red]",
            border_style="red",
        )
    )


def display_errors(errors: list[ValidationError]) -> None:
    if errors:
        CONSOLE.print("\n[bold red]Failed files:[/bold red]")
        for error in errors:
            CONSOLE.print(f"[red]✗ {error.file}:[/red] {error.reason}")


def display_summary(
    results: list[str | DataBaseModel],
    errors: list[ValidationError],
    output: str | None,
) -> None:
    total = len(results) + len(errors)
    success_rate = (len(results) / total * 100) if total > 0 else 0

    display_results(results)

    CONSOLE.print("\n[bold green]Processing Summary[/bold green]")
    CONSOLE.print(f"Total files processed: {total}")
    CONSOLE.print(
        f"Successfully processed: [blue]{len(results)} file(s) ({success_rate:.1f}%) / Failed: {len(errors)} file(s)[/blue]"
    )
    if output:
        CONSOLE.print(f"Output saved to: [blue]{output}[/blue]")

    display_errors(errors)

    CONSOLE.print("\n")
