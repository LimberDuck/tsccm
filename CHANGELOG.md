# Changelog

All notable changes to [**TSCCM** *(Tenable.SC CLI Manager)* by LimberDuck][1] project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.5] - 2025-09-01

### Added

#### CLI

- New option:
  - `tsccm --update-check` / `tsccm -u` - will return confirmation if you are using the latest version of TSCCM.

- Requirements update
  - from:
    - click>=8.1.8
    - keyring>=25.5.0
    - pyTenable>=1.6.0
    - oauthlib>=3.2.2
    - pandas>=2.0.3
  - to:
    - click>=8.2.1
    - keyring>=25.6.0
    - pyTenable>=1.8.3
    - oauthlib>=3.3.1
    - pandas>=2.3.2
  - new:
    - requests>=2.32.5

## [0.0.4] - 2025-02-22

### Changed

- code formatted with [black](https://black.readthedocs.io)
- requirements update
  - from:
    - click>=8.0.1
    - keyring>=23.1.0
    - pyTenable>=1.3.3
    - oauthlib>=3.1.1
    - pandas>=1.3.2
    - tabulate>=0.8.9
  - to:
    - click>=8.1.8
    - keyring>=25.5.0
    - pyTenable>=1.6.0
    - oauthlib>=3.2.2
    - pandas>=2.0.3
    - tabulate>=0.9.0

- tests for python
  - added: 3.10, 3.11, 3.12, 3.13
  - removed: 3.7

## [0.0.3] - 2021-08-26

### Added

- new format option to display data - `csv`
- `audit-file --list` command lists parameters `id`, `name`, `createdTime`, `modifiedTime`, `filename`, `originalFilename`

### Changed

- `user --list` command lists parameters `id`, `username`, `firstname`, `lastname`, `roleName`, `createdTime`, `modifiedTime`, `lastLogin`, `locked`, `failedLogins`
- `group --list` command lists parameters `id`, `name`, `createdTime`, `modifiedTime`, `userCount`
- `scan --list` command lists parameters `id`, `name`, `ownerUsername`, `createdTime`, `modifiedTime`, `scheduleType`, `scheduleEnabled`, `scheduleRepeatRule`, `scheduleStart`, `scheduleNextRun`
- `scan-result --list` command lists parameters `id`, `name`, `ownerUsername`, `createdTime`, `status`, `importStatus`, `totalIPs`, `scannedIPs`, `startTime`, `finishTime`, `scanDuration`
- `policy --list` command lists parameters `id`, `name`, `ownerUsername`, `createdTime`, `modifiedTime`, `policyTemplateName`
- `credential --list` command lists parameters `id`, `name`, `type`, `authType`, `ownerUsername`, `createdTime`, `modifiedTime`

## [0.0.2] - 2021-08-25

### Added

- `role --list` command lists parameters `id`, `name`, `createdTime`, `modifiedTime`, `organizationCounts`
- `--port` option to specify port number

### Changed

- `credential --list` command lists parameters `id`, `name`, `ownerUsername`, `createdTime`, `modifiedTime`
- `group --list` command lists parameters `id`, `name`, `createdTime`, `modifiedTime`
- `policy --list` command lists parameters `id`, `name`, `ownerUsername`, `createdTime`, `modifiedTime`
- `scan --list` command lists parameters `id`, `name`, `ownerUsername`, `createdTime`, `modifiedTime`
- `scan-result --list` command lists parameters `id`, `name`, `ownerUsername`, `createdTime`, `modifiedTime`
- `user --list` command lists parameters `id`, `username`, `firstname`, `lastname`, `roleName`, `createdTime`, `modifiedTime`, `lastLogin`
- `status` command renamed to `server`
- `server` options `--status`, `--ips`, `--version

## [0.0.1] - 2021-08-18

- initial release



[0.0.4]: https://github.com/LimberDuck/tsccm/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/LimberDuck/tsccm/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/LimberDuck/tsccm/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/LimberDuck/tsccm/releases/tag/v0.0.1

[1]: https://github.com/LimberDuck/tsccm
