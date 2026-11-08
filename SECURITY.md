# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | ✅ Yes             |
| < 0.1   | ❌ No              |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please report it **privately** to:

**security@example.com**

### What to Include

Please include the following information in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Any suggested fixes or mitigations
- Your contact information for follow-up

### Response Timeline

- **Acknowledgment**: Within 48 hours of receipt
- **Initial Assessment**: Within 5 business days
- **Fix Timeline**: Communicated after assessment (typically 30-90 days depending on severity)
- **Public Disclosure**: Coordinated with reporter after fix is released

## Security Practices

### Dependency Management

- **Dependabot** enabled for automated dependency updates
- Weekly scheduled updates with grouped PRs
- Security advisories monitored and patched promptly

### Code Security

- **CodeQL/Trivy scanning** in CI pipeline
- **Signed commits** required for maintainers
- **Secrets scanning** enabled (GitHub secret scanning)
- **No secrets in code** - use GitHub Environments/Secrets

### CI/CD Security

- Minimal permissions for CI jobs
- SARIF upload for security findings
- Separate release environment with protected secrets

### Platform-Specific Considerations

This project runs on Windows and accesses hardware sensors via:

- **WMI** (Windows Management Instrumentation) - requires admin for some queries
- **OpenHardwareMonitorLib** - third-party DLL, loaded via pythonnet
- **psutil** - cross-platform system utilities

#### Security Implications

- Admin privileges may be required for full sensor access
- Third-party DLL (OpenHardwareMonitorLib) should be verified (checksums)
- No network communication - purely local data collection
- Output files written to user-specified directory

## Vulnerability Disclosure Policy

1. **Private Disclosure**: Report vulnerabilities privately via email
2. **Coordinated Disclosure**: We work with reporters on timeline
3. **Credit**: Reporters acknowledged in release notes (if desired)
4. **No Legal Action**: We will not pursue legal action for good-faith research

## Security-Related Configuration

### Environment Variables

| Variable | Purpose | Security Note |
|----------|---------|---------------|
| `OPENHARDWAREMONITOR_DLL` | Path to OHM DLL | Verify DLL integrity; avoid untrusted paths |

### File Permissions

- Output logs: User-writable directory only
- Config files: Read-only for collector, writable for admin
- No sensitive data in logs (no passwords, tokens, PII)

## Contact

For security concerns, contact: **security@example.com**

For general questions, use [GitHub Issues](https://github.com/owner/repo/issues) with the "security" label.