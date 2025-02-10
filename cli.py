import argparse
import sys
from typing import List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from datetime import datetime

from file_processor.unstructured_processor import UnstructuredFileProcessor
from data_extractor.llm_extractor import LLMDataExtractor
from core.model_factory import ModelFactory

VERSION = "0.1-beta"
console = Console()

class RichHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=100)

    def start_section(self, heading):
        heading = f"\n[bold cyan]{heading}[/bold cyan]"
        super().start_section(heading)

    def _format_action(self, action):
        text = super()._format_action(action)
        text = text.replace('usage:', '[bold green]usage:[/bold green]')
        text = text.replace('options:', '[bold yellow]options:[/bold yellow]')
        return text

def print_banner():
    console.print(Panel.fit(
        "[bold blue]Document Information Extractor[/bold blue]\n"
        f"[cyan]Version {VERSION}[/cyan]",
        border_style="bright_blue",
        padding=(1, 2)
    ))

def parse_args(args: List[str]) -> argparse.Namespace:    
    parser = argparse.ArgumentParser(
        description="[bold]Extract structured data from documents[/bold]",
        formatter_class=RichHelpFormatter,
        epilog="""[bold green]Examples:[/bold green]
  # Basic usage with default settings
  %(prog)s contract.pdf
  
  # Specify languages and processing strategy
  %(prog)s contract.pdf --languages fr en --strategy accurate
  
  # Use a different LLM model
  %(prog)s contract.pdf --model gpt-4 --provider openai --temperature 0.2
  """
    )
    
    # Version information
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {VERSION}'
    )
    
    # File input arguments
    input_group = parser.add_argument_group('Input Configuration')
    input_group.add_argument(
        "input_file",
        help="Path to the document file to process (supported formats: PDF, DOCX, TXT)"
    )
    input_group.add_argument(
        "--languages",
        nargs="+",
        default=["fr"],
        help="List of languages to consider for document processing (default: %(default)s)"
    )
    input_group.add_argument(
        "--strategy",
        choices=["auto", "hi_res", "fast"],
        default="auto",
        help="Document processing strategy - 'auto' selects the best strategy (default: %(default)s)"
    )

    # LLM arguments
    llm_group = parser.add_argument_group('LLM Configuration')
    llm_group.add_argument(
        "--model",
        default="gemini-1.5-pro",
        help="LLM model name to use for extraction (default: %(default)s)"
    )
    llm_group.add_argument(
        "--provider",
        default="google-genai",
        help="LLM provider (e.g., google-genai, ollama) (default: %(default)s)"
    )
    llm_group.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="LLM temperature setting - lower values are more focused (default: %(default)s)"
    )

    # Model configuration
    config_group = parser.add_argument_group('Model Configuration')
    config_group.add_argument(
        "--examples",
        default="data/examples.json",
        help="Path to examples JSON file for few-shot learning (default: %(default)s)"
    )
    config_group.add_argument(
        "--model-schema",
        default="config/model.json",
        help="Path to model schema JSON file defining the extraction structure (default: %(default)s)"
    )

    # Output configuration
    output_group = parser.add_argument_group('Output Configuration')
    output_group.add_argument(
        "--output",
        help="Output file path (supported formats: CSV, JSON)",
        type=str
    )

    return parser.parse_args(args)

def main(args: List[str] = None) -> int:
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parse_args(args)

    try:
        print_banner()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            # Initialize components
            init_task = progress.add_task("[cyan]Initializing components...", total=1)
            
            processor = UnstructuredFileProcessor(
                file_path=parsed_args.input_file,
                languages=parsed_args.languages,
                strategy=parsed_args.strategy
            )
            extractor = LLMDataExtractor(
                model_name=parsed_args.model,
                provider=parsed_args.provider,
                temperature=parsed_args.temperature
            )
            progress.update(init_task, advance=1)

            # Load examples
            examples_task = progress.add_task("[green]Loading examples...", total=1)
            extractor.load_examples_json_file(parsed_args.examples)
            progress.update(examples_task, advance=1)

            # Load schema
            schema_task = progress.add_task("[yellow]Loading model schema...", total=1)
            model_json = ModelFactory.load_model_json_file(parsed_args.model_schema)
            output_model = ModelFactory.create_model(model_json)
            progress.update(schema_task, advance=1)

            # Process document
            process_task = progress.add_task("[magenta]Processing document...", total=1)
            text_content = processor.get_text_content()
            progress.update(process_task, advance=1)

            # Extract information
            extract_task = progress.add_task("[blue]Extracting information...", total=1)
            result = extractor.extract(text_content, output_model)
            progress.update(extract_task, advance=1)
        
        # Create a table for metadata with proper width
        table = Table(
            show_header=True,
            header_style="bold magenta",
            width=min(console.width, 120),
            highlight=True
        )
        table.add_column("Property", style="cyan", width=30)
        table.add_column("Value", style="green", width=None)
        
        table.add_row("Input File", parsed_args.input_file)
        table.add_row("Strategy", parsed_args.strategy)
        table.add_row("Languages", ", ".join(parsed_args.languages))
        table.add_row("Model", f"{parsed_args.provider}/{parsed_args.model}")
        
        console.print(table)
        console.print()

        # Display JSON result with proper wrapping
        json_str = result.model_dump_json(indent=2)
        console.print(Panel(
            Syntax(
                json_str,
                "json",
                theme="monokai",
                word_wrap=True,
                line_numbers=True
            ),
            title="[bold green]Extracted Data[/bold green]",
            border_style="green"
        ))

        # Write output if specified
        if parsed_args.output:
            try:
                ModelFactory.write_output(result, parsed_args.output)
                console.print(f"\n[bold green]Results written to:[/bold green] {parsed_args.output}")
            except Exception as e:
                console.print(f"\n[bold red]Error writing output:[/bold red] {str(e)}")
        
        return 0

    except Exception as e:
        console.print(Panel(
            f"[bold red]Error:[/bold red] {str(e)}",
            title="[bold red]Error occurred[/bold red]",
            border_style="red"
        ))
        return 1

if __name__ == "__main__":
    sys.exit(main())
