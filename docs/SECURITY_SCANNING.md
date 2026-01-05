# Security Scanning Configuration Guide

This document describes the vulnerability scanning configuration for the AI Model Pipelines project. We use a defense-in-depth approach with multiple scanning tools to maximize security coverage.

## Overview

The project implements comprehensive dependency vulnerability scanning using three complementary tools:

| Tool | Purpose | Database | Config File |
|------|---------|----------|-------------|
| **pip-audit** | Python package scanning | PyPI Advisory Database | `pyproject.toml` |
| **Safety** | Python security scanning | Safety DB (multi-source) | `.safety-policy.yml` |
| **Trivy** | Filesystem & container scanning | Multiple (NVD, etc.) | `trivy.yaml`, `.trivyignore` |

## Configuration Files

### 1. pip-audit Configuration (`pyproject.toml`)

pip-audit is configured in the `[tool.pip-audit]` section of `pyproject.toml`:

```toml
[tool.pip-audit]
vulnerability-service = "pypi"
require-hashes = false
format = "columns"
ignore-vulns = []
```

**Key Settings:**
- `vulnerability-service`: Which database to use (pypi, osv)
- `require-hashes`: Enable for production with requirements_lock.txt
- `ignore-vulns`: List of CVE IDs to ignore (with justification)

**Usage:**
```bash
# Scan requirements.txt
pip-audit --requirement requirements.txt

# Scan with config from pyproject.toml
pip-audit -r requirements.txt --desc --format table

# Generate JSON report
pip-audit -r requirements.txt --format json --output audit-results.json

# Generate SARIF report for GitHub Security tab
pip-audit -r requirements.txt --format sarif --output audit-results.sarif
```

### 2. Safety Configuration (`.safety-policy.yml`)

Safety uses a dedicated YAML policy file for configuration:

```yaml
version: "3.0"
security:
  fail-scan-with-severity: "low"
  continue-on-error: false
scan:
  requirements:
    - requirements.txt
ignore: []
```

**Key Settings:**
- `fail-scan-with-severity`: Minimum severity to fail builds (low, medium, high, critical)
- `ignore`: List of ignored vulnerabilities with justification
- `remediation`: Include fix recommendations in output

**Usage:**
```bash
# Scan with policy file
safety check --file requirements.txt

# Generate JSON output
safety check --file requirements.txt --json > safety-results.json

# Check specific package
safety check --package numpy==1.24.0
```

### 3. Trivy Configuration (`trivy.yaml`, `.trivyignore`)

Trivy uses two configuration files:
- `trivy.yaml`: Main configuration (scan settings, output format, policies)
- `.trivyignore`: Vulnerability IDs to ignore

**Key Settings (trivy.yaml):**
```yaml
scan:
  security-checks:
    - vuln
    - secret
vulnerability:
  severity:
    - CRITICAL
    - HIGH
    - MEDIUM
    - LOW
exit:
  code: 1  # Fail on vulnerabilities
```

**Ignore Format (.trivyignore):**
```
# CVE-ID: Justification | Expires: YYYY-MM-DD | Package: name==version
CVE-2023-12345
```

**Usage:**
```bash
# Scan filesystem with config
trivy fs --config trivy.yaml .

# Scan requirements file
trivy fs --scanners vuln requirements.txt

# Generate SARIF for GitHub Security
trivy fs --format sarif --output results.sarif .

# Scan with specific severity
trivy fs --severity HIGH,CRITICAL .
```

## Severity Levels & Response Policy

All scanners use consistent severity classifications:

| Severity | Description | Response Time | Action |
|----------|-------------|---------------|--------|
| **CRITICAL** | Actively exploited, RCE, auth bypass | Immediate | Block builds, patch ASAP |
| **HIGH** | Significant impact, commonly exploitable | 1 week | Block merges, must fix |
| **MEDIUM** | Moderate impact, specific conditions | 1 month | Warning, plan fix |
| **LOW** | Minor concerns, difficult to exploit | 3 months | Informational |

## Ignoring Vulnerabilities

### When to Ignore

Only ignore vulnerabilities when:
1. **Platform-specific**: Vulnerability doesn't affect your platform (e.g., Windows-only, you use Linux)
2. **Code path unused**: Affected functionality is not used (verify thoroughly)
3. **False positive**: Confirmed false positive (report to scanner maintainers)
4. **Temporary**: Waiting for upstream fix with mitigation in place

### How to Ignore

#### pip-audit (pyproject.toml)
```toml
[tool.pip-audit]
ignore-vulns = [
    # CVE-2023-12345: Only affects Windows, we use Linux | Review: 2026-06-01
    "CVE-2023-12345",
]
```

#### Safety (.safety-policy.yml)
```yaml
ignore:
  - id: "CVE-2023-12345"
    reason: "Only affects Windows systems; deployment is Linux-only"
    expires: "2026-06-01"
    package: "example-package"
    version: "==1.2.3"
```

#### Trivy (.trivyignore)
```
# CVE-2023-12345: Only affects Windows | Expires: 2026-06-01 | Package: pkg==1.0.0
CVE-2023-12345
```

### Required Documentation

Every ignored vulnerability **MUST** include:
1. **Vulnerability ID**: CVE or vulnerability identifier
2. **Justification**: Detailed reason why it's safe to ignore
3. **Expiry Date**: When to reconsider (max 6 months)
4. **Package & Version**: Affected dependency
5. **Review Ticket**: Link to tracking issue (if applicable)

## CI/CD Integration

The scanning tools are integrated into the GitHub Actions CI pipeline (`.github/workflows/ci.yml`):

```yaml
jobs:
  pip-audit-scan:
    # Scans Python dependencies with pip-audit

  safety-scan:
    # Scans Python dependencies with Safety

  trivy-scan:
    # Scans filesystem with Trivy
```

### Build Failure Policy

Builds fail when:
- Any vulnerability is detected (current strict policy)
- Severity threshold is exceeded (configurable)
- Scan errors occur (network issues, invalid config)

### Scan Artifacts

All scan results are saved as workflow artifacts:
- `pip-audit-results.txt` (human-readable)
- `pip-audit-results.json` (machine-readable)
- `pip-audit-results.sarif` (uploaded to GitHub Security tab)
- `safety-results.txt` (human-readable)
- `safety-results.json` (machine-readable)
- `trivy-results.txt` (human-readable)
- `trivy-results.json` (machine-readable)
- `trivy-results.sarif` (uploaded to GitHub Security tab)

Retention: 90 days

### GitHub Security Tab Integration

Vulnerability findings are automatically uploaded to the GitHub Security tab using SARIF format:

- **pip-audit**: Uploads findings to Security tab (category: `pip-audit`)
- **Trivy**: Uploads findings to Security tab (category: `trivy`)
- **Safety**: Results available in artifacts (SARIF not supported in free tier)

This provides centralized vulnerability management where you can:
- View all vulnerabilities across scanners in one place
- Track vulnerability trends over time
- Create security alerts for your repository
- Integrate with GitHub Advanced Security features

## Running Scans Locally

### Quick Start

```bash
# Install security tools
pip install pip-audit safety

# Run all scans
pip-audit -r requirements.txt --desc
safety check --file requirements.txt
trivy fs --config trivy.yaml .
```

### Before Committing

```bash
# Check for new vulnerabilities
./scripts/scan-dependencies.sh  # If script exists

# Or manually:
pip-audit -r requirements.txt && \
safety check --file requirements.txt && \
trivy fs .
```

### Generate SARIF Reports Locally

```bash
# pip-audit SARIF output
pip-audit -r requirements.txt --format sarif --output pip-audit.sarif

# Trivy SARIF output
trivy fs --config trivy.yaml --format sarif --output trivy.sarif .

# View SARIF in VS Code (with SARIF Viewer extension)
code pip-audit.sarif
```

## Updating Dependencies

### Safe Update Process

1. **Scan current state**:
   ```bash
   pip-audit -r requirements.txt --format json > before.json
   ```

2. **Update dependencies**:
   ```bash
   pip install --upgrade package-name
   pip freeze > requirements.txt
   ```

3. **Regenerate lock file**:
   ```bash
   pip-compile --generate-hashes requirements.txt > requirements_lock.txt
   ```

4. **Scan updated state**:
   ```bash
   pip-audit -r requirements.txt --format json > after.json
   safety check --file requirements.txt
   ```

5. **Compare results**:
   ```bash
   diff before.json after.json
   ```

6. **Test thoroughly** before committing

### Scheduled Scans

A separate scheduled workflow runs daily to detect newly disclosed vulnerabilities:
- Runs against main branch
- Creates GitHub issues for new findings
- Sends notifications (if configured)

See `.github/workflows/scheduled-security-scan.yml` (Phase 5)

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. Email security@example.com (or see SECURITY.md)
3. Include:
   - Package name and version
   - Vulnerability description
   - Scanner that detected it
   - Steps to reproduce

## Troubleshooting

### False Positives

If you believe a finding is a false positive:

1. **Verify thoroughly** - test the vulnerable code path
2. **Document your analysis** in the ignore comment
3. **Report to scanner maintainers**:
   - pip-audit: https://github.com/pypa/pip-audit/issues
   - Safety: https://github.com/pyupio/safety/issues
   - Trivy: https://github.com/aquasecurity/trivy/issues
4. **Set short expiry** (30-60 days) to recheck after database update

### Scan Failures

**Database update errors:**
```bash
# Clear cache and retry
rm -rf ~/.cache/pip-audit
rm -rf ~/.cache/trivy
```

**Timeout errors:**
```bash
# Increase timeout in configuration
# For Trivy: edit trivy.yaml timeout.scan
# For Safety: edit .safety-policy.yml scan.timeout
```

**Network errors in CI:**
```bash
# Check if proxy configuration is needed
# Add retry logic in workflow
```

## Best Practices

1. **Defense in Depth**: Use all three scanners for maximum coverage
2. **Regular Updates**: Update dependencies monthly at minimum
3. **Review Ignores**: Check ignored vulnerabilities weekly
4. **Document Everything**: All ignores must have clear justification
5. **Test Updates**: Always test after updating dependencies
6. **Stay Informed**: Subscribe to security advisories for your dependencies
7. **Automate**: Let CI catch issues before they reach production
8. **Respond Quickly**: Address CRITICAL/HIGH vulnerabilities within SLA
9. **Cross-Reference**: Compare results across all scanners
10. **Audit Trail**: Keep scan results for compliance

## Resources

### Documentation
- pip-audit: https://pypi.org/project/pip-audit/
- Safety: https://docs.safetycli.com/
- Trivy: https://aquasecurity.github.io/trivy/

### Vulnerability Databases
- PyPI Advisory Database: https://github.com/pypa/advisory-database
- Safety DB: https://github.com/pyupio/safety-db
- National Vulnerability Database: https://nvd.nist.gov/
- GitHub Security Advisories: https://github.com/advisories

### Security Resources
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE: https://cwe.mitre.org/
- CVE: https://cve.mitre.org/

## Support

For questions or issues with security scanning:
1. Check this documentation
2. Review scanner documentation
3. Check existing GitHub issues
4. Create a new issue with [Security] tag
5. Contact the security team

---

**Last Updated**: 2026-01-05
**Maintained By**: Security Team
**Review Cycle**: Quarterly
