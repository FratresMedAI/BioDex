# Security Policy

## Supported Versions

Security updates are provided for the latest stable release line (currently `1.x`).

## Reporting a Vulnerability

Please report vulnerabilities privately by opening a security advisory on GitHub:

- [GitHub Security Advisories](https://github.com/Fratres-X-Natura/BioDex/security/advisories)

Include:

- A clear description of the issue
- Reproduction steps or proof-of-concept
- Affected versions and environment details
- Any suggested mitigations

## Security posture

- BioDex is local-first and sends no telemetry by default.
- Audit logging is opt-in (`BIODEX_AUDIT_LOG=1`).
- Users are responsible for protecting local datasets, model weights, and export artifacts.

## Optional LLM (BYOK)

- AI review is optional and uses **your** API key (Bring Your Own Key).
- Keys are stored locally in `~/.cache/biodex/settings.json` as plain text.
- Keys are sent only to the LLM provider you choose (OpenAI, Anthropic, etc.) — never to BioDex or Fratres servers.
- Protect that file like any local credential; use **Clear** in the footer menu to remove saved keys.
