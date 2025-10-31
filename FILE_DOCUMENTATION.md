# Complete File Documentation

This document explains **every single file** in the TGPC repository, including hidden files and their purposes.

## 📁 Root Directory Files

### Essential Configuration Files

#### `pyproject.toml`
**Purpose**: Modern Python project configuration file (PEP 518/621 standard)
**Contains**:
- Project metadata (name, version, description)
- Dependencies list
- Build system configuration
- Entry points for CLI commands (`tgpc` command)
- Package discovery settings
**Why Essential**: Required for `pip install -e .` and modern Python packaging

#### `requirements.txt`
**Purpose**: Lists all Python dependencies needed to run the system
**Contains**: 6 essential packages:
- `requests`: HTTP requests to TGPC website
- `beautifulsoup4`: HTML parsing for data extraction
- `click`: Command-line interface framework
- `python-dotenv`: Environment variable loading
- `rich`: Beautiful terminal output
- `tenacity`: Retry mechanisms for failed requests
**Why Essential**: Ensures consistent dependency installation

#### `.env.example`
**Purpose**: Template for environment configuration
**Contains**: Optional configuration variables with examples
**Usage**: Copy to `.env` and customize for your environment
**Security**: Contains no actual secrets, just examples

#### `.gitignore`
**Purpose**: Tells Git which files to ignore (not track in version control)
**Contains**:
- Environment files (`.env`, `.env.local`)
- Temporary files (`*.tmp`, `*.temp`)
- Log files (`*.log`, `logs/`)
- Python cache files (`__pycache__/`)
- Backup files (`*.bak`, `*.backup`)
**Why Essential**: Prevents sensitive data and temporary files from being committed

#### `README.md`
**Purpose**: Main documentation and usage instructions
**Contains**: Installation, usage, and basic project information
**Why Essential**: First thing users see, explains how to use the system

### Data Directory

#### `data/rx.json`
**Purpose**: **YOUR VALUABLE DATA** - Main pharmacist dataset
**Contains**: 82,488+ pharmacist records with registration numbers, names, categories
**Size**: ~577,000 lines of JSON data
**Critical**: This is your core asset - all other files exist to work with this data

#### `backups/` (directory)
**Purpose**: Will store automatic backups when system creates them
**Current State**: Empty (backups created during operations)
**Why Exists**: Safety net for your valuable data

## 📁 Python Package (`tgpc/`)

### Package Root

#### `tgpc/__init__.py`
**Purpose**: Makes `tgpc` a Python package and defines public API
**Contains**:
- Package version and metadata
- Main imports (TGPCEngine, PharmacistRecord, Config)
- Public API definition
**Why Essential**: Required for Python package structure

### Command Line Interface (`tgpc/cli/`)

#### `tgpc/cli/__init__.py`
**Purpose**: Makes `cli` a Python subpackage
**Contains**: Imports for CLI components
**Why Essential**: Package structure requirement

#### `tgpc/cli/commands.py`
**Purpose**: **Main user interface** - All CLI commands
**Contains**:
- `tgpc total` - Get pharmacist count
- `tgpc extract` - Extract basic records
- `tgpc detailed` - Extract detailed information
- `tgpc sync` - Synchronize with website
**Why Essential**: This is how you interact with the system

### Core System (`tgpc/core/`)

#### `tgpc/core/__init__.py`
**Purpose**: Makes `core` a Python subpackage
**Contains**: Core component imports
**Why Essential**: Package structure requirement

#### `tgpc/core/engine.py`
**Purpose**: **Main orchestrator** - Coordinates all operations
**Contains**:
- TGPCEngine class (main system controller)
- Methods for extraction, saving, loading, syncing
- Component coordination logic
**Why Essential**: The brain of the system - everything flows through here

#### `tgpc/core/exceptions.py`
**Purpose**: Custom error handling for the system
**Contains**:
- TGPCException (base error class)
- NetworkException (web request errors)
- DataValidationException (data format errors)
- Other specific error types
**Why Essential**: Proper error handling and user feedback

### Data Extraction (`tgpc/extractors/`)

#### `tgpc/extractors/__init__.py`
**Purpose**: Makes `extractors` a Python subpackage
**Contains**: Extractor component imports
**Why Essential**: Package structure requirement

#### `tgpc/extractors/base.py`
**Purpose**: Base extractor class (if needed for inheritance)
**Status**: May be empty or contain base patterns
**Why Exists**: Extensibility for different extractor types

#### `tgpc/extractors/pharmacist_extractor.py`
**Purpose**: **Core data extraction logic** - Scrapes TGPC website
**Contains**:
- Web scraping logic
- HTML parsing
- Data extraction methods
- Request handling
**Why Essential**: This is what actually gets your data from the website

#### `tgpc/extractors/rate_limiter.py`
**Purpose**: **Prevents website blocking** - Controls request frequency
**Contains**:
- Rate limiting algorithms
- Adaptive delays
- Circuit breaker patterns
- Request throttling
**Why Essential**: Keeps you from being blocked by the TGPC website

### Data Models (`tgpc/models/`)

#### `tgpc/models/__init__.py`
**Purpose**: Makes `models` a Python subpackage
**Contains**: Data model imports
**Why Essential**: Package structure requirement

#### `tgpc/models/pharmacist.py`
**Purpose**: **Data structure definitions** - How pharmacist data is organized
**Contains**:
- PharmacistRecord class (main data structure)
- EducationRecord class (education information)
- WorkExperience class (work information)
- Data validation and serialization methods
**Why Essential**: Defines how your data is structured and validated

### Storage System (`tgpc/storage/`)

#### `tgpc/storage/__init__.py`
**Purpose**: Makes `storage` a Python subpackage
**Contains**: Storage component imports
**Why Essential**: Package structure requirement

#### `tgpc/storage/file_manager.py`
**Purpose**: **File operations** - Saves and loads your data
**Contains**:
- JSON file reading/writing
- Data serialization
- File path management
**Why Essential**: Handles saving your extracted data safely

### Configuration (`tgpc/config/`)

#### `tgpc/config/__init__.py`
**Purpose**: Makes `config` a Python subpackage
**Contains**: Configuration imports
**Why Essential**: Package structure requirement

#### `tgpc/config/settings.py`
**Purpose**: **System configuration** - All settings and options
**Contains**:
- Config class with all system settings
- Environment variable loading
- Default values
- Configuration validation
**Why Essential**: Controls how the system behaves

### Utilities (`tgpc/utils/`)

#### `tgpc/utils/__init__.py`
**Purpose**: Makes `utils` a Python subpackage
**Contains**: Utility imports
**Why Essential**: Package structure requirement

#### `tgpc/utils/logger.py`
**Purpose**: **Logging system** - Records what the system is doing
**Contains**:
- Logger configuration
- Log formatting
- Console and file output
**Why Essential**: Helps debug issues and track system activity

## 🔍 Hidden Files (Git Repository)

### `.git/` Directory
**Purpose**: Git version control system data
**Contains**: All Git history, branches, commits, and metadata
**Why Hidden**: Internal Git data, not meant for direct editing
**Critical**: Contains your entire project history

#### `.git/config`
**Purpose**: Git repository configuration
**Contains**: Remote URLs, branch settings, user preferences

#### `.git/HEAD`
**Purpose**: Points to current branch/commit
**Contains**: Reference to current checkout

#### `.git/index`
**Purpose**: Git staging area
**Contains**: Files staged for next commit

#### `.git/objects/`
**Purpose**: Git object database
**Contains**: All file contents, commits, trees (compressed)

#### `.git/refs/`
**Purpose**: Git references (branches, tags)
**Contains**: Pointers to commits for branches and tags

#### `.git/logs/`
**Purpose**: Git operation history
**Contains**: History of branch changes and operations

#### `.git/hooks/`
**Purpose**: Git hook scripts (automation triggers)
**Contains**: Sample scripts that can run on Git events
**Current State**: Only sample files, none active

### Python Cache Files

#### `__pycache__/` directories
**Purpose**: Python bytecode cache for faster loading
**Contains**: Compiled Python files (.pyc)
**Why Hidden**: Automatically generated, not source code
**Safe to Delete**: Python recreates them as needed

## 📊 File Importance Ranking

### 🔴 **CRITICAL** (Never Delete)
1. `data/rx.json` - Your valuable data
2. `tgpc/core/engine.py` - Main system logic
3. `tgpc/extractors/pharmacist_extractor.py` - Data extraction
4. `tgpc/cli/commands.py` - User interface

### 🟡 **ESSENTIAL** (Required for operation)
5. `pyproject.toml` - Package configuration
6. `requirements.txt` - Dependencies
7. `tgpc/models/pharmacist.py` - Data structures
8. `tgpc/config/settings.py` - System configuration
9. All `__init__.py` files - Package structure

### 🟢 **IMPORTANT** (Helpful but not critical)
10. `README.md` - Documentation
11. `.gitignore` - Git configuration
12. `tgpc/core/exceptions.py` - Error handling
13. `tgpc/storage/file_manager.py` - File operations

### ⚪ **OPTIONAL** (Can be regenerated)
14. `.env.example` - Configuration template
15. `__pycache__/` directories - Python cache
16. `backups/` directory - Will be created when needed

## 🔒 Security Notes

- No sensitive information is stored in any file
- `.env.example` contains only example values
- Actual secrets should go in `.env` (which is gitignored)
- All TGPC references are kept generic for security

## 🎯 Summary

**Total Files**: ~50+ files
**Essential Files**: 15 core files
**Your Data**: 1 critical file (`data/rx.json`)
**Hidden Files**: Git repository data + Python cache

Every file serves a specific purpose in making your TGPC data extraction system work efficiently and safely.