# Security Policy

## Reporting a Vulnerability

We take the security of our AI model pipeline project seriously. If you discover a security vulnerability, please help us protect our users by following responsible disclosure practices.

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them by emailing **dev[@]timoa.com**.

Include the following information in your report:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact and attack scenarios
- **Reproduction**: Step-by-step instructions to reproduce the issue
- **Environment**: Affected versions, OS, Python version, dependencies
- **Proof of Concept**: Code or commands demonstrating the issue (if applicable)
- **Suggested Fix**: If you have recommendations for remediation

### What to Expect

When you report a vulnerability:

1. **Acknowledgment**: We will acknowledge receipt within **48 hours**
2. **Updates**: We will provide regular updates on our progress (at least every 7 days)
3. **Validation**: We will validate and assess the severity of the vulnerability
4. **Fix Timeline**: We will work on a fix according to our severity-based response SLA (see below)
5. **Disclosure**: We will coordinate public disclosure timing with you
6. **Credit**: We will credit you in our security advisories (unless you prefer to remain anonymous)

### Response Timeline

Our response time depends on the severity of the vulnerability:

| Severity | Response Time | Fix Timeline | Description |
|----------|---------------|--------------|-------------|
| **CRITICAL** | 24 hours | Immediate | Actively exploited, remote code execution, authentication bypass |
| **HIGH** | 48 hours | 1 week | Significant impact, commonly exploitable, data exposure |
| **MEDIUM** | 1 week | 1 month | Moderate impact, specific conditions required |
| **LOW** | 2 weeks | 3 months | Minor concerns, difficult to exploit, minimal impact |

## Security Practices

### Automated Vulnerability Scanning

This project employs a **defense-in-depth** approach to dependency security using multiple automated scanning tools:

#### Continuous Integration Scanning

Every pull request and push to main is scanned by:

- **[pip-audit](https://pypi.org/project/pip-audit/)**: Scans Python dependencies against the PyPI Advisory Database (maintained by Python Packaging Authority)
- **[Safety](https://docs.safetycli.com/)**: Scans against Safety DB, which aggregates data from multiple sources including NVD, GitHub Security Advisories, and proprietary research
- **[Trivy](https://aquasecurity.github.io/trivy/)**: Multi-purpose scanner that checks filesystem, dependencies, and configurations for vulnerabilities

All scan results are:

- Uploaded as workflow artifacts (90-day retention)
- Integrated with GitHub Security tab via SARIF format
- Validated to fail builds on detected vulnerabilities

#### Scheduled Scanning

In addition to CI scans, we run **daily scheduled scans** at 2 AM UTC to detect newly disclosed vulnerabilities in our existing dependencies, even when code hasn't changed. These scans:

- Monitor the main branch continuously
- Create GitHub issues when new vulnerabilities are discovered
- Provide ongoing security monitoring between development cycles

For detailed technical configuration, see [docs/SECURITY_SCANNING.md](docs/SECURITY_SCANNING.md).

### Dependency Management Policy

#### Pinned Dependencies

We maintain strict dependency management:

- **requirements.txt**: Direct dependencies with version pins for reproducibility
- **requirements_lock.txt**: Complete dependency tree with SHA256 hashes for integrity verification
- **pyproject.toml**: Project metadata and development tool configurations

#### Update Policy

We follow a structured approach to dependency updates:

1. **Regular Updates**: Dependencies are reviewed monthly for available updates
2. **Security Updates**: Critical/high severity vulnerabilities are addressed immediately
3. **Testing**: All updates undergo thorough testing before merging
4. **Lock File Regeneration**: Lock files are regenerated after any dependency change
5. **Scan Verification**: All updates must pass vulnerability scans before deployment

#### Vulnerability Exception Process

Occasionally, we may need to temporarily ignore certain vulnerabilities (e.g., false positives, platform-specific issues, code paths not used). All exceptions:

- **MUST** include detailed justification
- **MUST** have an expiry date (maximum 6 months)
- **MUST** document the affected package and version
- **MUST** be reviewed regularly
- Are tracked in configuration files: `pyproject.toml`, `.safety-policy.yml`, `.trivyignore`

See [docs/SECURITY_SCANNING.md](docs/SECURITY_SCANNING.md) for the complete exception process.

### Build Security

#### CI/CD Pipeline

Our GitHub Actions workflows:

- Use pinned action versions (e.g., `actions/checkout@v4`, not `@main`)
- Run with minimal permissions (read-only by default)
- Validate all dependencies before use
- Generate Software Bill of Materials (SBOM) artifacts
- Upload security findings to GitHub Security tab

#### Secrets Management

- No secrets are committed to the repository
- Environment variables and GitHub Secrets are used for sensitive data
- Secret scanning is enabled via Trivy configuration
- `.gitignore` prevents accidental commits of common secret files (`.env`, `credentials.json`, etc.)

### Secure Coding Practices

We follow secure coding practices including:

- Input validation and sanitization
- Least privilege principles
- Defense in depth
- Regular security reviews
- OWASP Top 10 awareness

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
|---------|--------------------|
| main    | :white_check_mark: |
| < main  | :x:                |

As this is an active development project, we only support the latest main branch. We recommend always using the most recent version.

## Security Advisories

Security advisories are published through:

- GitHub Security Advisories (for this repository)
- Release notes (for security-related releases)
- Email notifications (for registered security contacts)

## Compliance & Standards

This project follows industry security standards and best practices:

- **OWASP Top 10**: Address common web application security risks
- **OWASP Dependency-Check**: Automated vulnerability scanning
- **NIST**: Follow NIST cybersecurity framework guidelines
- **CWE/CVE**: Track vulnerabilities using standard identifiers
- **CVSS**: Assess severity using Common Vulnerability Scoring System

## Third-Party Dependencies

Our security posture depends on the security of our dependencies. We use:

- **Python 3.11+**: With latest security patches
- **ML Frameworks**: PyTorch, scikit-learn, pandas, numpy
- **Data Processing**: pyarrow, pillow
- **Utilities**: requests, pydantic

All dependencies are:

- Scanned for known vulnerabilities
- Monitored for security advisories
- Updated regularly with security patches
- Pinned with hash verification

See `requirements.txt` and `requirements_lock.txt` for the complete dependency list.

## Security Resources

### Internal Documentation

- [Security Scanning Guide](docs/SECURITY_SCANNING.md) - Detailed scanner configuration and usage
- [CI/CD Workflow](.github/workflows/ci.yml) - Automated security scanning implementation
- [Scheduled Scans](.github/workflows/scheduled-vulnerability-scan.yml) - Daily vulnerability monitoring

### External Resources

- [PyPI Advisory Database](https://github.com/pypa/advisory-database)
- [Safety DB](https://github.com/pyupio/safety-db)
- [National Vulnerability Database](https://nvd.nist.gov/)
- [GitHub Security Advisories](https://github.com/advisories)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## Contact

For security-related questions or concerns:

- **Email**: dev[@]timoa.com
- **GitHub Security Advisories**: Use the "Security" tab to privately report vulnerabilities
- **General Issues**: Non-security bugs can be reported via GitHub Issues

## Acknowledgments

We appreciate the security research community's efforts in keeping our project secure. Security researchers who responsibly disclose vulnerabilities will be acknowledged in our security advisories (with their permission).

Thank you for helping keep our AI model pipeline project and our users safe!

---

**Last Updated**: 2026-01-05
**Policy Version**: 1.0
**Next Review**: 2026-04-05 (Quarterly review cycle)
