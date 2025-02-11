import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from langchain.callbacks.base import BaseCallbackHandler
from dotenv import load_dotenv

from core.utils import write_json, load_json_file, write_monitoring_data

load_dotenv()
MONITORING_FILE_PATH = os.getenv("MONITORING_FILE_PATH", "monitoring.json")
COST_MAPPING_PATH = os.getenv("COST_MAPPING_PATH", "config/cost_mapping.json")
TOKENS_INPUT_PRICING_UNIT = int(os.getenv("TOKENS_INPUT_PRICING_UNIT", 1000000))
TOKENS_OUTPUT_PRICING_UNIT = int(os.getenv("TOKENS_OUTPUT_PRICING_UNIT", 1000000))

class MonitoringCallbackHandler(BaseCallbackHandler):
    def __init__(self, model: str, provider: str):
        super().__init__()
        self.model = model
        self.provider = provider
        self.start_time = None
        self.end_time = None
        self.input_tokens = 0
        self.output_tokens = 0
        self._cost_mapping = load_json_file(COST_MAPPING_PATH)
        
    def on_llm_start(self, *args, **kwargs):
        self.start_time = datetime.now()

    def on_llm_end(self, *args, **kwargs):
        self._save_monitoring()

    def on_llm_error(self, error: str, *args, **kwargs):
        self._save_monitoring()

    def on_llm_new_token(self, token: str, *args, **kwargs):
        self.output_tokens += 1

    def _calculate_cost(self) -> float:
        provider_costs = self._cost_mapping.get(self.provider, self._cost_mapping["default"])
        model_costs = provider_costs.get(self.model, provider_costs.get("default"))
        
        return round(
            (self.input_tokens * model_costs["input"] / TOKENS_INPUT_PRICING_UNIT) +
            (self.output_tokens * model_costs["output"] / TOKENS_OUTPUT_PRICING_UNIT),
            4
        )

    def _get_monitoring_data(self) -> Dict[str, Any]:
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        return {
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "provider": self.provider,
            "duration_seconds": duration,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "estimated_cost_usd": self._calculate_cost()
        }

    def _save_monitoring(self):
        self.end_time = datetime.now()
        monitoring_file = Path(MONITORING_FILE_PATH)
        new_data = self._get_monitoring_data()
        write_monitoring_data(monitoring_file, new_data)
