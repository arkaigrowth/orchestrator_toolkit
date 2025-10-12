"""Pydantic models for folder migration operations."""
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class FolderMigrationConfig(BaseModel):
    """Configuration for folder migration operation."""

    old_path: Path = Field(description="Original folder path to migrate from")
    new_path: Path = Field(description="Target folder path to migrate to")
    backup_path: Optional[Path] = Field(default=None, description="Backup location for safety")
    dry_run: bool = Field(default=True, description="Preview changes without applying them")

    @field_validator('old_path')
    @classmethod
    def validate_old_exists(cls, v: Path) -> Path:
        """Ensure source path exists before migration."""
        if not v.exists():
            raise ValueError(f"Source path {v} does not exist")
        if not v.is_dir():
            raise ValueError(f"Source path {v} is not a directory")
        return v

    @field_validator('new_path')
    @classmethod
    def validate_no_conflict(cls, v: Path) -> Path:
        """Ensure target path doesn't already exist."""
        if v.exists():
            raise ValueError(f"Target path {v} already exists - cannot overwrite")
        return v


class FileReference(BaseModel):
    """Track a single file reference to be updated."""

    file_path: Path
    line_numbers: List[int] = Field(default_factory=list)
    old_pattern: str
    new_pattern: str
    context: str = Field(default="", description="Contextual information about the reference")


class MigrationResult(BaseModel):
    """Result of migration operation with detailed tracking."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    files_moved: int = Field(default=0, description="Number of files successfully moved")
    references_updated: int = Field(default=0, description="Number of references updated in code")
    backup_created: bool = Field(default=False, description="Whether backup was created")
    backup_location: Optional[Path] = Field(default=None, description="Path to backup")
    rollback_script: Optional[Path] = Field(default=None, description="Path to rollback script")
    issues: List[str] = Field(default_factory=list, description="Any issues encountered")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")
    success: bool = Field(default=False, description="Overall migration success status")

    def add_issue(self, issue: str) -> None:
        """Add an issue to the tracking list."""
        self.issues.append(issue)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning to the tracking list."""
        self.warnings.append(warning)


class MigrationPlan(BaseModel):
    """Complete migration plan with all necessary information."""

    config: FolderMigrationConfig
    files_to_update: List[FileReference] = Field(default_factory=list)
    validation_steps: List[str] = Field(default_factory=list)
    risk_level: str = Field(default="medium", pattern="^(low|medium|high)$")
    estimated_duration_minutes: int = Field(default=60, gt=0)

    def add_file_reference(self, ref: FileReference) -> None:
        """Add a file reference to the migration plan."""
        self.files_to_update.append(ref)

    @property
    def total_references(self) -> int:
        """Calculate total number of references to update."""
        return sum(len(ref.line_numbers) for ref in self.files_to_update)
