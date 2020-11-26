# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

### Changed

### Fixed

### Limitation

## [0.0.15] - 2020-11-26

### Added

- Added `license` to setup.py
- Added docker file to the generated Surround projects for `Jupyter` support
- Added support for creating a versioned output folder for each run that stores the log files.

### Changed

- Print available endpoints information to the console
- Updated the generated notebook to load data from a runner

### Fixed

- Allow CI to trigger on forked repositories
- Linting issue in generated project

## [0.0.14] - 2020-07-01

### Added

- Migrate from CircleCI to Codefresh
- Use sqlite3 for doit database

### Changed

- Simplify the assembler
- Add metrics to non predict pipelines
- Disable experimentation by default
- Add a description for the notebook task

### Fixed

- Update about and getting started link
