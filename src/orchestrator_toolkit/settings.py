from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import Optional

class OrchSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OTK_",
        env_file=None,
        case_sensitive=False,   # Accept otk_artifact_root too
        extra="ignore",         # Ignore unknown envs
    )

    # Accept relative or absolute; default ".ai_docs"
    artifact_root: Path = Field(default=Path(".ai_docs"), validation_alias="ARTIFACT_ROOT")

    # Derived paths
    tasks_dir: Path = Field(default_factory=lambda: Path(".ai_docs") / "tasks")
    plans_dir: Path = Field(default_factory=lambda: Path(".ai_docs") / "plans")

    # Adapters (keeping existing, but updating to use validation_alias)
    archon_enabled: bool = Field(default=False, validation_alias="ARCHON_ENABLED")
    archon_base_url: str = Field(default="http://localhost:8787", validation_alias="ARCHON_BASE_URL")
    archon_api_key: str = Field(default="", validation_alias="ARCHON_API_KEY")

    mem0_enabled: bool = Field(default=False, validation_alias="MEM0_ENABLED")
    mem0_api_url: str = Field(default="https://api.mem0.ai/v1", validation_alias="MEM0_API_URL")
    mem0_api_key: str = Field(default="", validation_alias="MEM0_API_KEY")

    def resolve_paths(self, cwd: Optional[Path] = None) -> None:
        """Make paths absolute (relative to repo cwd) and ensure directories exist."""
        base = cwd or Path.cwd()
        root = self.artifact_root
        if not root.is_absolute():
            root = (base / root).resolve()

        self.artifact_root = root
        self.tasks_dir = (root / "tasks").resolve()
        self.plans_dir = (root / "plans").resolve()

        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(cls) -> "OrchSettings":
        """Centralized loader that honors OTK_ARTIFACT_ROOT."""
        s = cls()  # reads env (OTK_ARTIFACT_ROOT) via validation_alias
        s.resolve_paths()
        return s