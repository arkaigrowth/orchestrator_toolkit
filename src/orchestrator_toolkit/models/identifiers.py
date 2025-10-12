"""
Pydantic models for ULI and slug-based identification system.

This module defines the data models for:
- ULI index records (storage and retrieval)
- Slug configuration (generation settings)
- Task and plan metadata (enhanced front matter)
- Migration state tracking (resumable migrations)

All models use Pydantic v2 for robust validation and serialization.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, Optional
from datetime import datetime
from enum import Enum
import re


# Type aliases for clarity
ULI = str  # 26-character ULID
Slug = str  # URL-safe slug (max 60 chars)
TaskID = str  # T-XXXX format
PlanID = str  # P-XXXX format


class MigrationPhase(str, Enum):
    """Phases of the migration state machine."""
    INITIALIZED = "initialized"
    BACKUP = "backup"
    TRANSFORM = "transform"
    RENAME = "rename"
    INDEX = "index"
    VALIDATE = "validate"
    COMPLETE = "complete"
    FAILED = "failed"


class ULIIndexRecord(BaseModel):
    """
    Single record in the ULI index.

    Represents a task or plan with its identifiers and metadata.
    Stored as a single line in claude/uli_index.jsonl.

    Validation guarantees:
    - ULI is exactly 26 characters using Crockford base32 alphabet
    - Slug is URL-safe (lowercase alphanumeric + hyphens)
    - ID follows T-XXXX or P-XXXX pattern
    - Path is a valid file path string
    - Created timestamp is ISO 8601 format

    Example:
        {
            "uli": "01J9YAVWN3Z7D3X3Z5E7WFT6A4",
            "type": "task",
            "id": "T-0042",
            "slug": "fix-auth-bug",
            "path": "ai_docs/tasks/T-0042--fix-auth-bug.md",
            "title": "Fix Auth Bug",
            "created": "2025-10-12T10:45:54.123Z"
        }
    """

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        str_strip_whitespace=True,
    )

    uli: ULI = Field(
        ...,
        min_length=26,
        max_length=26,
        pattern=r"^[0-9A-Z]{26}$",
        description="26-character ULID (time-sortable, globally unique)",
    )

    type: Literal["task", "plan"] = Field(
        ...,
        description="Type of artifact (task or plan)",
    )

    id: str = Field(
        ...,
        pattern=r"^[TP]-\d{4}$",
        description="Numeric ID (T-XXXX or P-XXXX)",
    )

    slug: Slug = Field(
        ...,
        min_length=1,
        max_length=60,
        pattern=r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$",
        description="URL-safe slug derived from title",
    )

    path: str = Field(
        ...,
        min_length=1,
        description="Relative path to file from repo root",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Human-readable title",
    )

    created: datetime = Field(
        ...,
        description="Creation timestamp (ISO 8601)",
    )

    @field_validator("uli")
    @classmethod
    def validate_uli_crockford(cls, v: str) -> str:
        """
        Validate ULI uses Crockford base32 alphabet.

        Crockford base32 excludes I, L, O, U to avoid ambiguity.
        Valid characters: 0-9, A-H, J-K, M-N, P-Z

        Raises:
            ValueError: If ULI contains invalid characters
        """
        if not re.match(r"^[0123456789ABCDEFGHJKMNPQRSTVWXYZ]{26}$", v):
            raise ValueError(
                "ULI must use Crockford base32 alphabet "
                "(0-9, A-H, J-K, M-N, P-Z, excludes I/L/O/U)"
            )
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug_format(cls, v: str) -> str:
        """
        Validate slug format rules.

        Rules:
        - Must start and end with alphanumeric
        - No consecutive hyphens
        - Only lowercase letters, numbers, and single hyphens

        Raises:
            ValueError: If slug violates format rules
        """
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug cannot start or end with hyphen")
        if "--" in v:
            raise ValueError("Slug cannot contain consecutive hyphens")
        return v


class SlugConfig(BaseModel):
    """
    Configuration for slug generation behavior.

    Allows customization of slug generation per project or command.

    Attributes:
        max_length: Maximum slug length (10-100 chars, default 60)
        separator: Character to use for word separation (- or _)
        lowercase: Convert to lowercase (default True)
        remove_unicode: Remove non-ASCII characters (default True)
        collision_suffix_format: Format string for collision suffixes (default "-{n}")

    Example:
        SlugConfig(max_length=40, separator="_", collision_suffix_format="_{n}")
    """

    max_length: int = Field(
        default=60,
        ge=10,
        le=100,
        description="Maximum slug length in characters",
    )

    separator: str = Field(
        default="-",
        pattern=r"^[-_]$",
        description="Separator character (hyphen or underscore)",
    )

    lowercase: bool = Field(
        default=True,
        description="Convert slug to lowercase",
    )

    remove_unicode: bool = Field(
        default=True,
        description="Remove non-ASCII characters",
    )

    collision_suffix_format: str = Field(
        default="-{n}",
        description="Format string for collision suffixes (e.g., -2, -3)",
    )

    @field_validator("collision_suffix_format")
    @classmethod
    def validate_suffix_format(cls, v: str) -> str:
        """Ensure suffix format contains {n} placeholder."""
        if "{n}" not in v:
            raise ValueError("collision_suffix_format must contain {n} placeholder")
        return v


class TaskMetadata(BaseModel):
    """
    Enhanced task front matter with ULI and slug.

    Extends the existing task metadata with new identification fields
    while maintaining backward compatibility.

    Required fields:
    - id: Numeric task ID (T-XXXX)
    - uli: Globally unique ULID
    - slug: Human-readable slug
    - title: Task title
    - owner: Task owner
    - status: Current task status
    - created: Creation timestamp

    Example:
        ---
        id: T-0042
        uli: 01J9YAVWN3Z7D3X3Z5E7WFT6A4
        slug: fix-auth-bug
        title: Fix Auth Bug
        owner: alice
        status: in-progress
        created: 2025-10-12T10:45:54.123Z
        ---
    """

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        str_strip_whitespace=True,
    )

    id: TaskID = Field(
        ...,
        pattern=r"^T-\d{4}$",
        description="Numeric task ID (T-XXXX)",
    )

    uli: ULI = Field(
        ...,
        min_length=26,
        max_length=26,
        description="Globally unique ULID",
    )

    slug: Slug = Field(
        ...,
        max_length=60,
        description="Human-readable URL-safe slug",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title",
    )

    owner: str = Field(
        ...,
        min_length=1,
        description="Task owner (username or identifier)",
    )

    status: Literal["new", "assigned", "in-progress", "blocked", "done"] = Field(
        ...,
        description="Current task status",
    )

    created: datetime = Field(
        ...,
        description="Creation timestamp",
    )


class PlanMetadata(BaseModel):
    """
    Enhanced plan front matter with ULI and slug.

    Extends the existing plan metadata with new identification fields.
    Plans can optionally reference a parent task.

    Required fields:
    - id: Numeric plan ID (P-XXXX)
    - uli: Globally unique ULID
    - slug: Human-readable slug
    - title: Plan title
    - owner: Plan owner
    - status: Current plan status
    - created: Creation timestamp

    Optional fields:
    - task: Parent task ID (T-XXXX)

    Example:
        ---
        id: P-0007
        uli: 01J9YB5K8F2Q9P7X3M6N4R8S2T
        slug: auth-migration-plan
        task: T-0042
        title: Auth Migration Plan
        owner: alice
        status: in-progress
        created: 2025-10-12T11:00:00.000Z
        ---
    """

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        str_strip_whitespace=True,
    )

    id: PlanID = Field(
        ...,
        pattern=r"^P-\d{4}$",
        description="Numeric plan ID (P-XXXX)",
    )

    uli: ULI = Field(
        ...,
        min_length=26,
        max_length=26,
        description="Globally unique ULID",
    )

    slug: Slug = Field(
        ...,
        max_length=60,
        description="Human-readable URL-safe slug",
    )

    task: Optional[TaskID] = Field(
        default=None,
        pattern=r"^T-\d{4}$",
        description="Parent task ID (optional)",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Plan title",
    )

    owner: str = Field(
        ...,
        min_length=1,
        description="Plan owner (username or identifier)",
    )

    status: Literal["draft", "ready", "in-progress", "complete", "abandoned"] = Field(
        ...,
        description="Current plan status",
    )

    created: datetime = Field(
        ...,
        description="Creation timestamp",
    )


class MigrationState(BaseModel):
    """
    Persistent state for resumable migrations.

    Tracks migration progress and allows interruption and resumption
    of long-running migrations. Saved to claude/migration_state.json.

    Attributes:
        phase: Current migration phase
        started: When migration started
        updated: Last update timestamp
        files_processed: Number of files processed so far
        total_files: Total number of files to process
        backup_dir: Path to backup directory
        errors: List of error messages encountered

    Example:
        {
            "phase": "transform",
            "started": "2025-10-12T10:00:00.000Z",
            "updated": "2025-10-12T10:05:30.000Z",
            "files_processed": 42,
            "total_files": 100,
            "backup_dir": "claude/backups/migration_20251012_100000",
            "errors": []
        }
    """

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
    )

    phase: MigrationPhase = Field(
        ...,
        description="Current phase of migration",
    )

    started: datetime = Field(
        ...,
        description="Migration start timestamp",
    )

    updated: datetime = Field(
        ...,
        description="Last update timestamp",
    )

    files_processed: int = Field(
        default=0,
        ge=0,
        description="Number of files processed",
    )

    total_files: int = Field(
        ...,
        gt=0,
        description="Total number of files to process",
    )

    backup_dir: str = Field(
        ...,
        min_length=1,
        description="Path to backup directory",
    )

    errors: list[str] = Field(
        default_factory=list,
        description="List of error messages",
    )

    @field_validator("files_processed")
    @classmethod
    def validate_progress(cls, v: int, info) -> int:
        """Ensure files_processed doesn't exceed total_files."""
        # Note: info.data is the validated data so far
        if "total_files" in info.data and v > info.data["total_files"]:
            raise ValueError("files_processed cannot exceed total_files")
        return v

    @property
    def progress_percentage(self) -> float:
        """Calculate migration progress as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.files_processed / self.total_files) * 100

    @property
    def is_complete(self) -> bool:
        """Check if migration is complete."""
        return self.phase == MigrationPhase.COMPLETE

    @property
    def has_errors(self) -> bool:
        """Check if migration has encountered errors."""
        return len(self.errors) > 0
