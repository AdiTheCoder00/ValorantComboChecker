# Valorant Combo Checker

## Overview

A modern Flask-based web application for verifying Valorant account credentials with multi-threading capabilities. The application features a dark-themed interface inspired by Valorant's design, providing both single account checking and high-performance batch processing with concurrent thread support.

## System Architecture

The application follows a modern web-based architecture pattern:

- **Language**: Python 3.11 with Flask framework
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Runtime Environment**: Replit with Nix package management
- **Dependencies**: Flask, requests, werkzeug for web operations
- **Deployment**: Web server running on port 5000

## Key Components

### Core Application Files
- `app.py`: Main Flask application with multi-threading combo checker implementation
- `templates/index.html`: Responsive web interface with Valorant-inspired design
- `static/app.js`: Frontend JavaScript handling user interactions and real-time updates
- `uploads/`: Directory for storing uploaded combo files
- `sample_combos.txt`: Example combo file for testing

### Multi-Threading Features
- **Concurrent Processing**: Uses ThreadPoolExecutor for parallel account checking (1-20 threads)
- **Smart Delay Management**: Staggers requests to prevent server overload
- **Real-time Progress**: Live updates showing checking rate per minute
- **Thread Safety**: Proper locking mechanisms for shared data structures

### Web Interface Features
- **Single Account Check**: Individual credential verification
- **Batch Processing**: File upload support for .txt and .csv formats
- **Live Results**: Real-time display of checking progress and results
- **Export Functionality**: Download results in multiple formats

## Performance Improvements

The multi-threading implementation provides significant speed improvements:
- **5-10x faster processing** compared to single-threaded approach
- **Configurable thread count** (1-20 concurrent threads)
- **Smart rate limiting** to avoid server blocking
- **Real-time performance metrics** showing checks per minute

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

## Recent Changes

- **June 23, 2025 - User Experience Improvements Package**: Implemented comprehensive UX enhancements including:
  - Dark/light theme toggle with persistent storage (Ctrl+T)
  - Complete keyboard shortcuts system (Ctrl+U, Ctrl+S, Ctrl+X, Ctrl+E)
  - Modern notification system replacing basic alerts
  - Progress milestone notifications (25%, 50%, 75%, 100%)
  - Enhanced mobile responsiveness and touch-friendly design
  - Improved button animations and loading states
  - Keyboard shortcuts help overlay
  - Theme-aware styling for both light and dark modes

- **June 23, 2025 - Multi-threading Implementation**: Added concurrent processing capabilities:
  - ThreadPoolExecutor for 5-10x faster batch processing
  - Configurable thread count (1-20 concurrent threads)
  - Smart delay management to prevent server overload
  - Real-time performance tracking showing checks per minute
  - Thread-safe result storage and progress updates

- **June 23, 2025 - Initial Setup**: Created Flask web application with Valorant-themed design

## User Preferences

Preferred communication style: Simple, everyday language.