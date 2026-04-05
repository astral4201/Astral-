"""Configuration loader for Astral."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


def load_config(config_path: str | Path | None = None) -> dict:
    """Load configuration from YAML file and environment variables."""
    load_dotenv()

    if config_path is None:
        config_path = Path(__file__).parents[3] / "config.yaml"

    config_path = Path(config_path)
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}

    # Inject env vars
    config.setdefault("macro", {})
    config["macro"]["fred_api_key"] = os.getenv("FRED_API_KEY", "")

    return config
