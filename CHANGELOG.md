# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Two-tier semantic caching architecture (Exact Match SQLite + Semantic FAISS)
- Cost-savings observability dashboard via Streamlit
- Production-grade caching engine for LLMs
- Precise cost tracking and analytics
- Support for multiple LLM providers

### Changed

### Deprecated

### Removed

### Fixed

### Security

---

## Release Notes

For detailed release notes and version history, please see the [Releases](https://github.com/aaminashihab/semantic-cache/releases) page.

## Version History

### [0.1.0] - 2024-01-XX

#### Added
- Initial release of semantic-cache
- Two-tier caching system implementation
- Exact match caching with SQLite backend
- Semantic caching with FAISS integration
- Streamlit-based observability dashboard
- Cost-savings analytics and reporting
- Comprehensive test suite
- Docker support

#### Features
- High-performance semantic similarity search
- Configurable cache thresholds and parameters
- Real-time cost tracking
- Integration with popular LLM APIs
- RESTful API for cache operations
- Batch processing support

---

## Guidelines for Maintainers

When releasing a new version:

1. Update version numbers in relevant files
2. Update this CHANGELOG.md file with the new version and changes
3. Create a git tag with the version number
4. Push the tag to trigger release workflows
5. Create a release on GitHub with release notes

## How to Contribute to This Changelog

Please note that we maintain this changelog for all contributions. If you're submitting a PR:

1. Include a CHANGELOG entry describing your changes
2. Follow the format: `- [Category] Brief description of change`
3. Place your entry in the Unreleased section
4. Use present tense and imperative mood
