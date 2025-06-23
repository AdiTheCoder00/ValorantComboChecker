# Valorant Combo Checker

## Overview

This is a Python-based Valorant account credential verification tool that checks the validity of username/password combinations. The application is designed to run in a Replit environment with minimal dependencies, using only the `requests` library for HTTP operations.

## System Architecture

The application follows a simple, single-file architecture pattern:

- **Language**: Python 3.11
- **Runtime Environment**: Replit with Nix package management
- **Dependencies**: Minimal - only `requests` library for HTTP operations
- **Deployment**: Direct execution via shell commands

## Key Components

### Core Application
- `main.py`: Main application entry point (not visible in repository but referenced in workflows)
- **Logging**: Uses `combo_checker.log` for application logging
- **Package Management**: UV lock file for dependency resolution and `pyproject.toml` for project configuration

### Configuration Files
- `.replit`: Defines the Replit environment and workflow configurations
- `pyproject.toml`: Python project metadata and dependency specifications
- `uv.lock`: Dependency lock file ensuring reproducible builds

## Data Flow

1. **Input**: Account credentials (username/password combinations)
2. **Processing**: HTTP requests to validate credentials against Valorant's authentication system
3. **Output**: Validation results logged to `combo_checker.log`

The application operates in a batch processing mode, likely reading credentials from a file or input source and outputting results to the log file.

## External Dependencies

### Primary Dependencies
- **requests (>=2.32.4)**: HTTP library for making authentication requests
- **certifi**: SSL certificate validation
- **charset-normalizer**: Text encoding normalization

### Runtime Environment
- **Python 3.11**: Runtime environment
- **Nix (stable-24_05)**: Package management system
- **Replit**: Cloud development and execution platform

## Deployment Strategy

The application uses a simple deployment strategy optimized for Replit:

1. **Dependency Installation**: Automatic pip installation of requests library
2. **Execution**: Direct Python script execution via shell commands
3. **Workflow**: Parallel execution model with named workflows for organization

### Deployment Commands
```bash
pip install requests && python main.py
```

## Changelog

- June 23, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.