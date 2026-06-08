# Security Policy

## Supported Versions

Security updates are provided for the latest stable release line (currently `1.x`).

## Reporting a Vulnerability

Please report vulnerabilities privately by opening a security advisory on GitHub:

- [GitHub Security Advisories](https://github.com/FratresMedAI/BioDex/security/advisories)

Include:

- A clear description of the issue
- Reproduction steps or proof-of-concept
- Affected versions and environment details
- Any suggested mitigations

## Security posture

- BioDex is local-first and sends no telemetry by default.
- Audit logging is opt-in (`BIODEX_AUDIT_LOG=1`).
- Users are responsible for protecting local datasets, model weights, and export artifacts.
