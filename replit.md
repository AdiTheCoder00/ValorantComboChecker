# Valorant Account Combo Checker

## Overview

This is a Python-based GUI application designed for checking Valorant account combinations with batch processing capabilities. The application provides both single account verification and bulk combo checking functionality through a user-friendly Tkinter interface. The tool is explicitly designed for educational and legitimate testing purposes only, with strong emphasis on ethical usage.

## System Architecture

### Frontend Architecture
- **GUI Framework**: Tkinter with ttk for modern widget styling
- **Interface Pattern**: Tabbed interface using `ttk.Notebook`
- **Threading Model**: Separate worker threads for combo checking to prevent GUI freezing
- **User Interaction**: Modal dialogs for disclaimers and file operations

### Backend Architecture
- **Core Logic**: Modular design with separate classes for different responsibilities
- **Request Handling**: Session-based HTTP requests using the `requests` library
- **Rate Limiting**: Configurable delays between authentication attempts
- **Error Handling**: Comprehensive exception handling with logging

### Application Structure
```
main.py              # Entry point with disclaimer and app initialization
gui.py               # GUI components and user interface logic
combo_checker.py     # Core authentication checking functionality
config.py            # Configuration constants and settings
utils.py             # Utility functions for validation and data processing
```

## Key Components

### 1. Main Application (`main.py`)
- **Purpose**: Application entry point and legal disclaimer handling
- **Features**: Logging setup, disclaimer acceptance dialog
- **Architecture Decision**: Separate entry point for clean initialization and legal compliance

### 2. GUI Interface (`gui.py`)
- **Purpose**: Complete user interface implementation
- **Features**: Tabbed interface, progress tracking, file operations
- **Architecture Decision**: Single class handling all GUI operations for simplicity

### 3. Combo Checker (`combo_checker.py`)
- **Purpose**: Core authentication verification logic
- **Features**: Session management, rate limiting, result tracking
- **Architecture Decision**: Stateful class design to maintain session and results

### 4. Configuration (`config.py`)
- **Purpose**: Centralized configuration management
- **Features**: Rate limiting, GUI settings, file formats, endpoints
- **Architecture Decision**: Single configuration file for easy maintenance

### 5. Utilities (`utils.py`)
- **Purpose**: Helper functions for data validation and processing
- **Features**: Email validation, password strength checking
- **Architecture Decision**: Stateless utility functions for reusability

## Data Flow

1. **Application Startup**: User accepts disclaimer → GUI initialization
2. **Single Check Flow**: User input → Validation → Authentication request → Result display
3. **Batch Check Flow**: File selection → Parsing → Threaded checking → Progress updates → Result export
4. **Result Management**: In-memory storage → Optional file export (TXT/CSV)

## External Dependencies

### Core Dependencies
- **requests**: HTTP client for authentication requests
- **tkinter**: Built-in GUI framework (no external dependency)

### Authentication Endpoints
- **Riot Games Auth API**: `https://auth.riotgames.com/api/v1/authorization`
- **Rate Limiting**: Configurable delays (1-10 seconds) to respect server limits

### File System Integration
- **Input Formats**: TXT and CSV files with various separators
- **Output Formats**: TXT and CSV for result export
- **Logging**: File-based logging with rotation

## Deployment Strategy

### Environment Requirements
- **Python Version**: 3.7+ (configured for 3.11 in Replit)
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Dependencies**: Minimal external dependencies for easy deployment

### Replit Configuration
- **Module**: Python 3.11 with Nix package management
- **Workflow**: Automated dependency installation and execution
- **Deployment**: Direct execution with `pip install requests && python main.py`

### Installation Process
1. Clone/download repository
2. Install dependencies: `pip install requests`
3. Execute: `python main.py`

## Changelog

- June 23, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.