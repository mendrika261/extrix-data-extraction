import argparse
import sys
from typing import List, Type, Tuple, NamedTuple
from pydantic import BaseModel
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.syntax import Syntax
from pathlib import Path

from file_processor.unstructured_processor import UnstructuredFileProcessor
from data_extractor.llm_extractor import LLMDataExtractor
from core.model_factory import ModelFactory
from core.utils import find_files

VERSION = "0.1-beta"
console = Console()

class ProcessingError(NamedTuple):
    file: Path
    reason: str

class Processor:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.extractor = self._init_extractor()
        self.output_model = self._init_model()
        self.processor_args = {
            "languages": args.languages,
            "strategy": args.strategy,
            "use_cache": not args.no_cache
        }
        
    def _init_extractor(self) -> LLMDataExtractor:
        extractor = LLMDataExtractor(
            model_name=self.args.model,
            provider=self.args.provider,
            temperature=self.args.temperature
        )
        extractor.load_examples_json_file(self.args.examples)
        return extractor
    
    def _init_model(self) -> Type[BaseModel]:
        model_json = ModelFactory.load_model_json_file(self.args.model_schema)
        return ModelFactory.create_model(model_json)

    def process_file(self, file_path: Path, progress: Progress) -> Tuple[BaseModel, ProcessingError]:
        try:
            # Create nested progress tasks for file processing stages
            file_task = progress.add_task(
                f"[blue]File:[/blue] {file_path.name}",
                total=2
            )
            
            # Stage 1: Text extraction
            progress.update(file_task, description=f"[blue]Extracting text from {file_path.name}[/blue]")
            processor = UnstructuredFileProcessor(
                file_path=str(file_path),
                **self.processor_args
            )
            text_content = processor.get_text_content()
            progress.update(file_task, advance=1)
            
            # Stage 2: Data extraction
            progress.update(file_task, description=f"[blue]Extracting data from {file_path.name}[/blue]")
            result = self.extractor.extract(text_content, self.output_model)
            progress.update(file_task, advance=1)
            
            if self.args.output:
                try:
                    ModelFactory.write_output(result, self.args.output)
                except Exception as e:
                    console.print(f"[yellow]Warning: Failed to write output for {file_path}[/yellow]")
            
            progress.remove_task(file_task)
            return result, None
            
        except Exception as e:
            if 'file_task' in locals():
                progress.remove_task(file_task)
            return None, ProcessingError(file_path, str(e))

    def display_result(self, result: BaseModel) -> None:
        console.print(Panel(
            Syntax(
                result.model_dump_json(indent=2),
                "json",
                theme="monokai",
                word_wrap=True,
                line_numbers=True
            ),
            border_style="green"
        ))

def display_summary(successful: int, errors: List[ProcessingError]) -> None:
    console.print("\n[bold green]Processing complete![/bold green]")
    console.print(f"Successfully processed: {successful} file(s)")
    
    if errors:
        console.print("\n[bold red]Failed files:[/bold red]")
        for error in errors:
            console.print(f"[red]• {error.file}:[/red] {error.reason}")
    console.print("\n")

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
  
  # Process multiple files using glob pattern
  %(prog)s "contracts/*.pdf"
  
  # Specify languages and processing strategy
  %(prog)s "data/*.pdf" --languages fr en --strategy accurate
  
  # Use a different LLM model
  %(prog)s "docs/*.pdf" --model gpt-4 --provider openai --temperature 0.2
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
        "input_pattern",
        help="Path or glob pattern for document files to process (supported formats: PDF, DOCX, TXT)"
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
    input_group.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching for text extraction"
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
            # Initialize extractor and model
            init_task = progress.add_task("[cyan]Initializing...", total=1)
            processor = Processor(parsed_args)
            progress.update(init_task, advance=1, completed=True)

            # Find files to process
            files = find_files(parsed_args.input_pattern)
            if not files:
                console.print(f"[bold red]No files found matching pattern:[/bold red] {parsed_args.input_pattern}")
                return 1

            # Process files with progress tracking
            overall_task = progress.add_task(
                "[yellow]Overall progress",
                total=len(files)
            )
            
            successful = 0
            errors: List[ProcessingError] = []
            
            for file_path in files:
                result, error = processor.process_file(file_path, progress)

                console.print(f"\n[bold blue]Results for:[/bold blue] {file_path}")
                if error:
                    console.print(f"[red]Failed:[/red] {error.reason}")
                    errors.append(error)
                else:
                    processor.display_result(result)
                    successful += 1
                
                progress.update(overall_task, advance=1)

            progress.update(overall_task, description="[green]Processing complete!")
            display_summary(successful, errors)
            return 0 if successful > 0 else 1

    except Exception as e:
        console.print(Panel(
            f"[bold red]Error:[/bold red] {str(e)}",
            title="[bold red]Error occurred[/bold red]",
            border_style="red"
        ))
        return 1

if __name__ == "__main__":
    sys.exit(main())
