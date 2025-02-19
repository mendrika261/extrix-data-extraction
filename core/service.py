import os
from pathlib import Path
from cli.ui import CONSOLE
from core.exceptions import ValidationError
from core.model_factory import ModelFactory
from core.models import DataBaseModel
from core.utils import write_csv, write_json
from data_extractor.data_extractor import DataExtractor
from data_extractor.llm_extractor import LLMDataExtractor
from text_extractor.text_extractor import TextExtractor
from text_extractor.unstructured import Strategy, UnstructuredTextExtractor
from core.queue_manager import QueueManager
from time import sleep

from web.models import ExtractorConfig


queue_manager = None


def _get_text_extractor(text_extractor: str) -> type[TextExtractor]:
    if text_extractor == "unstructured":
        return UnstructuredTextExtractor
    raise ValueError(f"Unknown text extractor: {text_extractor}")


def extract_text(
    file_path: Path,
    languages: list[str],
    strategy: Strategy,
    no_cache: bool,
    text_extractor: str,
) -> str:
    extractor_class = _get_text_extractor(text_extractor)
    extractor = extractor_class(languages, not no_cache, strategy)
    return extractor.get_text_content(file_path)


def _get_data_extractor(data_extractor: str) -> type[DataExtractor]:
    if data_extractor == "llm":
        return LLMDataExtractor
    raise ValueError(f"Unknown data extractor: {data_extractor}")


def extract_data(
    text_content: str,
    output_schema: type[DataBaseModel],
    data_extractor: str,
    **kwargs,
) -> DataBaseModel:
    extractor_class = _get_data_extractor(data_extractor)
    extractor = extractor_class(**kwargs)
    return extractor.extract(text_content, output_schema)


def extract(
    file_path: Path,
    languages: list[str],
    strategy: Strategy,
    no_cache: bool,
    text_extractor: str,
    output_schema: type[DataBaseModel],
    data_extractor: str,
    output: str | None = None,
    **kwargs,
) -> str | DataBaseModel | ValidationError:
    global queue_manager
    queue_manager = QueueManager(kwargs["max_items"], kwargs["time_limit"])

    while not queue_manager.can_process():
        CONSOLE.print(
            f"Limit per minute is reached. Waiting for {queue_manager.time_limit} minutes..."
        )
        sleep(queue_manager.time_limit * 60)

    queue_manager.increment_processed()

    try:
        text_content = extract_text(
            file_path, languages, strategy, no_cache, text_extractor
        )
        extracted_data = extract_data(
            text_content, output_schema, data_extractor, **kwargs
        )

        if output is not None:
            extension = output.split(".")[-1]
            if extension == "csv":
                write_csv(Path(output), extracted_data.model_dump_csv())
            elif extension == "json":
                write_json(Path(output), extracted_data.model_dump())

        return extracted_data
    except Exception as e:
        return ValidationError(file_path, str(e))


def extract_list(
    files_path: list[Path],
    languages: list[str],
    strategy: Strategy,
    no_cache: bool,
    text_extractor: str,
    output_schema: type[DataBaseModel],
    data_extractor: str = "llm",
    output: str | None = None,
    progress=None,
    **kwargs,
) -> tuple[list[str | DataBaseModel], list[ValidationError]]:
    results = []
    errors = []

    total_files = len(files_path)
    task_id = None
    if progress:
        task_id = progress.add_task("Processing files...", total=total_files)

    for file_path in files_path:
        if progress:
            progress.update(task_id, description=f"Processing {file_path.name}")

        result = extract(
            file_path,
            languages,
            strategy,
            no_cache,
            text_extractor,
            output_schema,
            data_extractor,
            output,
            **kwargs,
        )
        if isinstance(result, ValidationError):
            errors.append(result)
        else:
            results.append(result)

        if progress:
            progress.advance(task_id)

    return results, errors


def extract_from_config_file(
    files_path: list[Path],
    languages: list[str],
    strategy: Strategy,
    no_cache: bool,
    text_extractor: str,
    output_schema_path: Path,
    data_extractor: str = "llm",
    output: str | None = None,
    **kwargs,
) -> tuple[list[str | DataBaseModel], list[ValidationError]]:
    output_schema = ModelFactory.load_model_json_file(output_schema_path)
    return extract_list(
        files_path,
        languages,
        strategy,
        no_cache,
        text_extractor,
        output_schema,
        data_extractor,
        output,
        **kwargs,
    )


def extract_from_config(
    file_path: Path,
    config: ExtractorConfig,
) -> DataBaseModel | ValidationError:
    try:
        output_schema = ModelFactory.load_model_json(config.output_schema)

        kwargs = {
            "llm_model": config.llm_model,
            "llm_provider": config.llm_provider,
            "llm_temperature": config.llm_temperature,
            "examples": config.examples,
            "max_items": int(os.getenv("QUEUE_MAX_ITEMS", "60")),
            "time_limit": int(os.getenv("QUEUE_TIME_LIMIT_MINUTES", "1")),
        }

        return extract(
            file_path=file_path,
            languages=config.languages,
            strategy=config.strategy,  # Remove Strategy() conversion since it's already an enum
            no_cache=config.no_cache,
            text_extractor=config.text_extractor,
            output_schema=output_schema,
            data_extractor=config.data_extractor,
            output=None,
            **kwargs,
        )
    except Exception as e:
        return ValidationError(file_path, str(e))
