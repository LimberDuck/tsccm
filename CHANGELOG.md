# Changelog

All notable changes to [**TSCCM** *(Tenable.SC CLI Manager)* by LimberDuck][1] project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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



[0.0.3]: https://github.com/LimberDuck/tsccm/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/LimberDuck/tsccm/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/LimberDuck/tsccm/releases/tag/v0.0.1

[1]: https://github.com/LimberDuck/tsccm
