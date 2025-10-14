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

    # NEW: Configurable docs folder name (default without dot for visibility)
    docs_folder: str = Field(
        default="ai_docs",
        validation_alias="DOCS_FOLDER",
        description="Name of documentation folder (ai_docs for visibility, .ai_docs for hidden)"
    )

    # Accept relative or absolute; default uses docs_folder
    # LEGACY: artifact_root can still override everything for backward compatibility
    artifact_root: Optional[Path] = Field(
        default=None,
        validation_alias="ARTIFACT_ROOT",
        description="Legacy override for artifact location"
    )

    # Derived paths - computed based on docs_folder or artifact_root
    tasks_dir: Path = Field(default_factory=lambda: Path("ai_docs") / "tasks")
    plans_dir: Path = Field(default_factory=lambda: Path("ai_docs") / "plans")
    specs_dir: Path = Field(default_factory=lambda: Path("ai_docs") / "specs")
    exec_logs_dir: Path = Field(default_factory=lambda: Path("ai_docs") / "exec_logs")

    # ULI/Slug Configuration (NEW for T-0001)
    slug_max_length: int = Field(
        default=60,
        validation_alias="SLUG_MAXLEN",
        ge=10,
        le=100,
        description="Maximum slug length (default: 60 chars)"
    )

    index_dir: str = Field(
        default="claude",
        validation_alias="INDEX_DIR",
        description="Directory for ULI index (default: claude/)"
    )

    use_ulid: bool = Field(
        default=True,
        validation_alias="USE_ULID",
        description="Use ULID format for ULIs (default: true)"
    )

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

        # Determine effective root: artifact_root (legacy) or docs_folder (new)
        if self.artifact_root is not None:
            # Legacy mode: artifact_root takes precedence
            root = self.artifact_root
        else:
            # New mode: use docs_folder
            root = Path(self.docs_folder)

        if not root.is_absolute():
            root = (base / root).resolve()

        self.artifact_root = root
        self.tasks_dir = (root / "tasks").resolve()
        self.plans_dir = (root / "plans").resolve()
        self.specs_dir = (root / "specs").resolve()
        self.exec_logs_dir = (root / "exec_logs").resolve()

        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.specs_dir.mkdir(parents=True, exist_ok=True)
        self.exec_logs_dir.mkdir(parents=True, exist_ok=True)

        # Ensure index directory exists (NEW for ULI system)
        index_path = Path(self.index_dir)
        if not index_path.is_absolute():
            index_path = (base / index_path).resolve()
        index_path.mkdir(parents=True, exist_ok=True)

    @property
    def index_path(self) -> Path:
        """Full path to ULI index file."""
        return Path(self.index_dir) / "uli_index.jsonl"

    @property
    def index_lock_path(self) -> Path:
        """Full path to index lock file."""
        return Path(self.index_dir) / "uli_index.lock"

    @classmethod
    def load(cls) -> "OrchSettings":
        """Centralized loader that honors OTK_ARTIFACT_ROOT."""
        s = cls()  # reads env (OTK_ARTIFACT_ROOT) via validation_alias
        s.resolve_paths()
        return s
