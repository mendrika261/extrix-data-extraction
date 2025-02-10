from pathlib import Path
from typing import List, Tuple, Type, Dict
from rich.syntax import Syntax
from rich.panel import Panel
from pydantic import BaseModel

from cli.models import ProcessingError
from cli.ui import CONSOLE as console
from data_extractor.llm_extractor import LLMDataExtractor
from core.model_factory import ModelFactory
from core.utils import load_classes_from_package
from file_processor.interface import FileProcessor
from rich.progress import Progress

class CliProcessor:
    def __init__(self, args):
        self.args = args
        self.extractor = self._init_extractor()
        self.output_model = self._init_model()
        self.file_processors = self._load_all_file_processors()

        self.file_processor_class = self.file_processors.get(self.args.processor)
        if not self.file_processor_class:
            raise ValueError(f"Unknown file processor: {self.args.processor}")
        
        
    def _load_all_file_processors(self) -> Dict[str, Type[FileProcessor]]:
        return load_classes_from_package(
            package_name='file_processor',
            base_class=FileProcessor,
            module_suffix='_processor',
            exclude_base=True
        )

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

    def _process_file(self, file_path: Path, progress: Progress, task_id: int) -> BaseModel:
        try:
            self.file_processor = self.file_processor_class(
                file_path=str(file_path),
                languages=self.args.languages,
                use_cache=not self.args.no_cache,
                **({"strategy": self.args.strategy} if self.args.processor == "unstructured" else {})
            )

            progress.update(task_id, description=f"[yellow]Extracting text content from {file_path}[/yellow]")
            text_content = self.file_processor.get_text_content()

            progress.update(task_id, description=f"[yellow]Extracting data from text content of {file_path}[/yellow]")
            result = self.extractor.extract(text_content, self.output_model)
            
            if self.args.output:
                try:
                    ModelFactory.write_output(result, self.args.output)
                except Exception as e:
                    console.print(f"[yellow]Warning: Failed to write output for {file_path}[/yellow]")

            progress.update(task_id, description=f"[green]Processing complete for {file_path}[/green]")
            return result, None
            
        except Exception as e:
            return None, ProcessingError(file_path, str(e))

    
    def process_files(self, files: List[Path], progress: Progress) -> Tuple[int, List[ProcessingError]]:
        total_files = len(files)
        overall_task = progress.add_task(
            f"[yellow]Processing {total_files} files",
            total=total_files,
            start=True
        )
        successful = 0
        errors: List[ProcessingError] = []
        
        for index, file_path in enumerate(files, 1):            
            result, error = self._process_file(file_path, progress, overall_task)
            
            console.print(f"\n[bold blue]Results for:[/bold blue] {file_path}")                

            if result and not error:
                self._display_result(result)
                successful += 1
            else:
                console.print(f"[red]Failed:[/red] {error.reason if error else 'Unknown error'}")
                errors.append(error)
            

            progress.update(overall_task, completed=index)
        
        progress.update(overall_task, description="[green]All files processed!")
        
        return successful, errors


    def _display_result(self, result: BaseModel) -> None:
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
