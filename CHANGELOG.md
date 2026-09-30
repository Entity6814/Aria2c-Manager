# Changelog

All notable changes to Aria2c Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern PyQt6 GUI with dark theme and browser-like interface
- Chrome/Edge extension for download interception
- System tray integration with background operation
- Crash resistance with persistent download state
- Configurable download locations via extension settings
- Smart notifications for download events
- Inline download controls (pause/resume/cancel)
- Real-time progress monitoring and speed display
- Professional documentation (README, INSTALL, CONTRIBUTING)
- MIT License for open source distribution

### Changed
- Optimized aria2c configuration for multi-threaded downloads (16 connections, 16 splits)
- Improved filename handling to preserve file extensions
- Enhanced error handling and user feedback
- Better download location management

### Fixed
- Unicode encoding issues on Windows
- PyQt6 event handling compatibility
- Chrome notification API requirements
- Download selection preservation during GUI refresh
- Clear completed downloads functionality
- RPC URL format compatibility with aria2c

## [1.0.0] - 2024-09-29

### Added
- Initial release of Aria2c Manager
- aria2c RPC daemon launcher (start_aria2.py)
- PyQt6 desktop GUI application (app.pyw)
- Manifest V3 browser extension (extension/)
- Multi-threaded download support
- Browser download interception
- Basic download management UI
- System tray integration
- Download state persistence
- Notification system
- Cross-platform support (Windows/Linux/Mac)

### Security
- Default RPC secret token (should be changed in production)
- HTTPS support for secure downloads
- File permission handling

### Documentation
- Comprehensive README with features and usage
- Installation guide for all platforms
- Contributing guidelines for developers
- MIT License

[Unreleased]: https://github.com/Entity6814/Aria2c-Manager/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Entity6814/Aria2c-Manager/releases/tag/v1.0.0
