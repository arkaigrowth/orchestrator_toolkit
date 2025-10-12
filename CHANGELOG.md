# Changelog

All notable changes to the Orchestrator Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-12

### 🚀 Major Features

#### ULI and Slug System
- **Globally Unique IDs**: Implemented ULID-based ULI (Universally Unique Lexicographically Sortable Identifier) system
- **Human-Readable Slugs**: Added slug generation from titles for better file discovery
- **Time-Sortable**: ULIs are chronologically sortable by creation time
- **Collision Resolution**: Deterministic `-2`, `-3` suffix handling for duplicate slugs
- **Performance**: O(1) cached lookups with JSONL index

#### Folder Visibility Fix
- **BREAKING CHANGE**: Renamed `.ai_docs` to `ai_docs` for IDE visibility
- **IDE Autocomplete**: Now works with `ai_docs/tasks/T-` and `ai_docs/plans/P-`
- **Migration Support**: Automatic migration script included
- **Backward Compatibility**: Use `OTK_ARTIFACT_ROOT=.ai_docs` to keep old behavior

### ✨ New Features
- Added `uli.py` module for ULI generation and validation
- Added `slug.py` module for Unicode-safe slug generation
- Added `index_manager.py` for thread-safe index operations
- Enhanced `id_alloc.py` with filename deduplication
- Comprehensive Pydantic v2 models for all data structures
- 35+ unit tests with 100% coverage on critical paths

### 🔧 Improvements
- Settings now support configurable `docs_folder` (default: `ai_docs`)
- Settings support configurable `slug_max_length` (10-100 chars, default 60)
- Settings support configurable `index_dir` (default: `claude/`)
- Added migration models in `models/migration.py`
- Added identifier models in `models/identifiers.py`

### 📦 Dependencies
- Added `ulid-py>=1.1,<2` for ULID generation
- Added `filelock>=3.0,<4` for thread-safe file operations
- Updated to `pydantic-settings>=2.3,<3`

### 🔄 Migration Guide

#### From 1.x to 2.0.0

1. **Folder Migration** (BREAKING CHANGE):
   ```bash
   # Option 1: Use migration script
   python scripts/migrate_docs_folder.py

   # Option 2: Manual migration
   mv .ai_docs ai_docs

   # Option 3: Keep old behavior
   export OTK_ARTIFACT_ROOT=.ai_docs
   ```

2. **New Environment Variables**:
   ```bash
   # Customize folder name (default: ai_docs)
   export OTK_DOCS_FOLDER=my_docs

   # Customize slug length (default: 60)
   export OTK_SLUG_MAXLEN=80

   # Customize index location (default: claude/)
   export OTK_INDEX_DIR=index/
   ```

### 🐛 Bug Fixes
- Fixed IDE autocomplete not working with hidden folders
- Fixed file discovery issues in various tools
- Improved error handling in settings resolution

### 📚 Documentation
- Added comprehensive architecture documentation
- Updated README with new folder structure
- Added migration guides and rollback procedures
- Documented all Pydantic models

### 🧪 Testing
- Added 35 comprehensive tests for ULI/slug system
- Full test coverage for migration scenarios
- Performance benchmarks for index operations

### ⚠️ Breaking Changes
- Default artifact folder changed from `.ai_docs` to `ai_docs`
- Requires migration for existing projects (script provided)
- Minimum Python version remains 3.10

### 🙏 Acknowledgments
- Thanks to Chad for the comprehensive integration plans
- Thanks to Alex for driving the v2.0 roadmap

---

## [1.0.1] - 2025-10-12

### Added
- PyPI Test package support
- Comprehensive installation test script
- Example usage documentation

### Fixed
- Package metadata for PyPI
- Installation instructions

## [1.0.0] - 2025-10-11

### Initial Release
- Core task and plan management system
- CLI commands: `task-new`, `plan-new`, `orchestrator-once`
- Pydantic-based settings management
- Integration hooks for Mem0 and Archon
- Comprehensive documentation

---

For more details, see the [GitHub releases](https://github.com/arkaigrowth/orchestrator_toolkit_1.0/releases).