import argparse
from typing import List


class RichHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=100)

    def start_section(self, heading):
        heading = f"\n[bold cyan]{heading}[/bold cyan]"
        super().start_section(heading)

    def _format_action(self, action):
        text = super()._format_action(action)
        text = text.replace("usage:", "[bold green]usage:[/bold green]")
        text = text.replace("options:", "[bold yellow]options:[/bold yellow]")
        return text


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="[bold]Extract structured data from documents[/bold]",
        formatter_class=RichHelpFormatter,
    )

    input_group = parser.add_argument_group("Input Configuration")
    input_group.add_argument(
        "files_path", help="Path or glob pattern for document files"
    )
    input_group.add_argument(
        "--languages",
        nargs="+",
        default=["fr"],
        help="List of languages (default: %(default)s)",
    )
    input_group.add_argument(
        "--strategy", choices=["auto", "hi_res", "fast"], default="auto"
    )
    input_group.add_argument(
        "--no-cache", action="store_true", help="Disable cache for OCR results"
    )
    input_group.add_argument(
        "--text-extractor",
        choices=["unstructured"],
        default="unstructured",
    )

    llm_group = parser.add_argument_group("LLM Configuration")
    llm_group.add_argument(
        "--data-extractor",
        default="llm",
        help="Data extractor to use for information extraction (default: %(default)s)",
    )
    llm_group.add_argument(
        "--llm-model",
        default="gemini-1.5-pro",
        help="LLM model name to use for extraction (default: %(default)s)",
    )
    llm_group.add_argument(
        "--llm-provider",
        default="google-genai",
        help="LLM provider (e.g., google-genai, ollama) (default: %(default)s)",
    )
    llm_group.add_argument(
        "--llm-temperature",
        type=float,
        default=0.1,
        help="LLM temperature setting - lower values are more focused (default: %(default)s)",
    )

    config_group = parser.add_argument_group("Model Configuration")
    config_group.add_argument(
        "--examples-path",
        default="data/examples.json",
        help="Path to examples JSON file for few-shot learning (default: %(default)s)",
    )
    config_group.add_argument(
        "--output-schema-path",
        default="config/model.json",
        help="Path to model schema JSON file defining the extraction structure (default: %(default)s)",
    )

    output_group = parser.add_argument_group("Output Configuration")
    output_group.add_argument(
        "--output",
        help="Output file path (supported formats: CSV, JSON)",
        type=str,
    )

    queue_group = parser.add_argument_group("Queue Configuration")
    queue_group.add_argument(
        "--max-items",
        type=int,
        default=60,
        help="Maximum number of items to process in given time limit (default: %(default)s)",
    )
    queue_group.add_argument(
        "--time-limit",
        type=int,
        default=1,
        help="Time limit for maximum number of items in minutes (default: %(default)s)",
    )

    return parser.parse_args(args)
