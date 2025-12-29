import yaml
import os
from pathlib import Path
from typing import Dict
from pydantic import BaseModel, validator


class WeightsConfig(BaseModel):
    crime_weight: float = 0.25
    infrastructure_weight: float = 0.25
    demographic_weight: float = 0.25
    sentiment_weight: float = 0.25

    @validator('crime_weight', 'infrastructure_weight', 'demographic_weight', 'sentiment_weight')
    def validate_weights(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Weights must be between 0 and 1")
        return v

    def validate_sum(self):
        total = (
            self.crime_weight +
            self.infrastructure_weight +
            self.demographic_weight +
            self.sentiment_weight
        )
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return True


def load_weights_config(config_path: str = None) -> WeightsConfig:
    """Load weights configuration from YAML file or use defaults"""
    if config_path is None:
        config_path = os.path.join(
            Path(__file__).parent.parent,
            "config",
            "weights.yaml"
        )

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            weights = WeightsConfig(**config_data)
    else:
        # Use defaults if config file doesn't exist
        weights = WeightsConfig()

    weights.validate_sum()
    return weights

