from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppCfg(BaseModel):
    name: str = "Chain Digital — Monad Risk Scanner"
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"


class ChainCfg(BaseModel):
    id: str = "monad-mainnet"
    confirmations: int = 0


class RpcCfg(BaseModel):
    url: str
    timeout_seconds: float = 10.0
    max_retries: int = 5


class DbCfg(BaseModel):
    url: str


class ScannerCfg(BaseModel):
    poll_interval_seconds: float = 3.0
    max_blocks_per_tick: int = 5
    backfill_start_block: Optional[int] = None


class AnalysisCfg(BaseModel):
    ordering_sensitivity: bool = True
    conflict_patterns: bool = True
    hot_state: bool = True
    hidden_dependencies: bool = True


class SignalsCfg(BaseModel):
    min_severity_to_store: int = 20


class FileConfig(BaseModel):
    app: AppCfg = AppCfg()
    chain: ChainCfg = ChainCfg()
    rpc: RpcCfg
    db: DbCfg
    scanner: ScannerCfg = ScannerCfg()
    analysis: AnalysisCfg = AnalysisCfg()
    signals: SignalsCfg = SignalsCfg()


class Settings(BaseSettings):
    # Path to YAML config (mounted in Docker)
    config_path: str = Field(default="configs/config.yaml", alias="SCANNER_CONFIG")

    model_config = SettingsConfigDict(extra="ignore")

    def load(self) -> FileConfig:
        p = Path(self.config_path)
        if not p.exists():
            raise FileNotFoundError(
                f"Config not found: {p}. Create it from configs/config.example.yaml"
            )
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return FileConfig.model_validate(data)
