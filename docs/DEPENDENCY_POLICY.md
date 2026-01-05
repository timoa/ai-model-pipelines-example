# Dependency Update Policy

This document defines the operational policy for managing Python dependencies in the AI Model Pipelines project. It establishes clear expectations for update frequency, vulnerability response procedures, and exception governance.

## Overview

Effective dependency management is critical for maintaining the security and stability of our AI model training pipeline. This policy ensures we:

- **Stay Secure**: Respond promptly to vulnerability disclosures
- **Stay Current**: Regularly update dependencies to avoid technical debt
- **Stay Stable**: Test thoroughly before deploying updates
- **Stay Compliant**: Document all decisions and maintain audit trails

This policy complements our automated scanning infrastructure (see [SECURITY_SCANNING.md](SECURITY_SCANNING.md)) and security practices (see [../SECURITY.md](../SECURITY.md)).

## Dependency Update Policy

### Update Types

We distinguish between several types of dependency updates:

| Update Type | Definition | Priority | Testing Required |
|-------------|------------|----------|------------------|
| **Security Patch** | Addresses known vulnerability (CVE) | CRITICAL/HIGH/MEDIUM/LOW (varies) | Regression + Security |
| **Bug Fix** | Fixes bugs without new features | Medium | Regression |
| **Minor Version** | New features, backward compatible | Low | Full test suite |
| **Major Version** | Breaking changes, new features | Low | Comprehensive testing |
| **Transitive** | Dependency of dependency | Same as direct | Same as direct |

### Update Frequency

#### Scheduled Updates

We follow a regular update schedule:

| Frequency | Scope | Schedule | Responsible |
|-----------|-------|----------|-------------|
| **Monthly** | All dependencies review | First Tuesday of each month | Development Team |
| **Quarterly** | Major version updates (planned) | Beginning of each quarter | Tech Lead + Team |
| **Daily** | Automated vulnerability scans | 2 AM UTC (automated) | CI/CD System |
| **Continuous** | CI scanning on every PR/push | On commit (automated) | CI/CD System |

#### Ad-Hoc Updates

Outside of scheduled updates, we perform updates when:

1. **Critical/High vulnerabilities** are disclosed (see response SLAs below)
2. **Critical bugs** affect production or block development
3. **Security advisories** are published for our dependencies
4. **Upstream deprecation** notices require action

### Update Process

All dependency updates must follow this process:

#### 1. Review Phase
```bash
# Check current state
pip list --outdated
pip-audit -r requirements.txt --desc

# Review changelogs for target packages
# Identify breaking changes and security fixes
# Assess compatibility risks
```

#### 2. Update Phase
```bash
# Update specific package(s)
pip install --upgrade package-name==X.Y.Z

# Or update multiple packages
pip install --upgrade -r requirements.txt

# Freeze updated dependencies
pip freeze > requirements.txt
```

#### 3. Lock File Regeneration
```bash
# Regenerate lock file with hashes
pip-compile --generate-hashes requirements.txt -o requirements_lock.txt

# Verify lock file integrity
pip-audit -r requirements_lock.txt
```

#### 4. Testing Phase
```bash
# Run full test suite
pytest tests/

# Run security scans
pip-audit -r requirements.txt --desc
safety check --file requirements.txt
trivy fs .

# Perform integration testing
# Test affected functionality
```

#### 5. Documentation Phase
- Update CHANGELOG.md with dependency changes
- Document any breaking changes in commit message
- Update this policy if new practices are adopted
- Record decision rationale for major updates

#### 6. Deployment Phase
```bash
# Create PR with changes
git checkout -b update-dependencies-YYYY-MM-DD
git add requirements.txt requirements_lock.txt
git commit -m "chore: update dependencies (YYYY-MM-DD)

- Updated [package] from X.Y.Z to A.B.C (security fix for CVE-XXXX)
- Updated [package] from X.Y.Z to A.B.C (bug fix)
- All tests passing
- Security scans clean"

git push origin update-dependencies-YYYY-MM-DD
# Create PR and wait for CI validation
```

### Pre-Commit Checklist

Before committing dependency updates:

- [ ] Lock file regenerated with `pip-compile --generate-hashes`
- [ ] All security scans pass (pip-audit, safety, trivy)
- [ ] Full test suite passes
- [ ] Integration tests pass for affected components
- [ ] Changelog updated
- [ ] Commit message documents all changes
- [ ] No new vulnerabilities introduced
- [ ] Breaking changes documented and communicated

## Vulnerability Response SLAs

When vulnerabilities are detected by our scanning tools, we follow severity-based response procedures.

### CRITICAL Severity

**Definition**: Actively exploited, remote code execution (RCE), authentication bypass, privilege escalation with easy exploit path.

**Examples**:
- CVE with public exploit code actively used in the wild
- Remote code execution requiring no authentication
- Authentication bypass in core libraries

**Response SLA**: **24 hours** (response) | **Immediate** (fix deployment)

**Required Actions**:

1. **Hour 0-1**: Initial Assessment
   - Security team notified immediately (email + Slack alert)
   - Verify vulnerability applies to our usage
   - Assess blast radius and affected systems
   - Create emergency response ticket

2. **Hour 1-4**: Immediate Mitigation
   - Apply temporary workarounds if available
   - Consider taking affected systems offline if actively exploited
   - Implement network-level controls if applicable
   - Update WAF rules or firewall policies

3. **Hour 4-24**: Permanent Fix
   - Update vulnerable dependency to patched version
   - Regenerate lock files with hashes
   - Run all security scans
   - Deploy to staging for validation
   - Deploy to production after minimal testing (security overrides stability)

4. **Hour 24-48**: Post-Incident
   - Document incident and response actions
   - Conduct post-mortem review
   - Update policies based on lessons learned
   - Notify stakeholders of resolution

**Approval**: Security Team Lead (or on-call engineer)

**Testing**: Minimal regression testing only (security > stability for CRITICAL)

**Communication**: Immediate notification to all stakeholders

### HIGH Severity

**Definition**: Significant impact, commonly exploitable, data exposure, authentication issues without immediate exploit.

**Examples**:
- SQL injection with specific conditions
- Cross-site scripting (XSS) vulnerabilities
- Sensitive data exposure
- Denial of service with simple exploit

**Response SLA**: **48 hours** (response) | **1 week** (fix deployment)

**Required Actions**:

1. **Day 1**: Assessment & Planning
   - Security team reviews vulnerability details
   - Verify applicability to our codebase
   - Review exploit prerequisites and attack vectors
   - Create response ticket with priority label
   - Assign owner for remediation

2. **Day 2-3**: Fix Development
   - Identify patched version or workaround
   - Test update in development environment
   - Run full test suite
   - Verify vulnerability is resolved
   - Document changes

3. **Day 4-5**: Testing & Validation
   - Deploy to staging environment
   - Run integration tests
   - Perform security validation
   - Review with security team
   - Obtain approval for production deployment

4. **Day 6-7**: Deployment & Verification
   - Deploy to production during maintenance window
   - Monitor for issues post-deployment
   - Verify vulnerability no longer detected
   - Update documentation
   - Close response ticket

**Approval**: Development Team Lead + Security Review

**Testing**: Full regression testing required

**Communication**: Notify stakeholders within 48 hours, update before deployment

### MEDIUM Severity

**Definition**: Moderate impact, specific conditions required, limited scope, defense-in-depth improvements.

**Examples**:
- Information disclosure requiring specific conditions
- Vulnerabilities in development dependencies only
- Denial of service requiring complex conditions
- Moderate security improvements

**Response SLA**: **1 week** (response) | **1 month** (fix deployment)

**Required Actions**:

1. **Week 1**: Triage & Assessment
   - Review vulnerability during weekly security review
   - Assess impact and exploitability
   - Determine if workarounds are available
   - Add to monthly update backlog
   - Prioritize relative to other work

2. **Week 2-3**: Include in Next Update Cycle
   - Bundle with other dependency updates
   - Schedule for monthly maintenance window
   - Develop and test fix
   - Document changes

3. **Week 4**: Deployment
   - Include in monthly update deployment
   - Standard testing and validation
   - Deploy during regular maintenance window
   - Verify resolution

**Approval**: Standard PR review process

**Testing**: Full test suite + integration tests

**Communication**: Include in monthly security report

### LOW Severity

**Definition**: Minor concerns, difficult to exploit, minimal impact, informational findings.

**Examples**:
- Vulnerabilities in unused code paths (confirmed)
- Theoretical vulnerabilities with no known exploit
- Minor information disclosure with no sensitive data
- Best practice recommendations

**Response SLA**: **2 weeks** (response) | **3 months** (fix deployment)

**Required Actions**:

1. **Month 1**: Review & Documentation
   - Review during monthly dependency review
   - Document finding and rationale
   - Determine if action is needed
   - Consider for quarterly update

2. **Month 2-3**: Include in Quarterly Updates
   - Bundle with quarterly major updates
   - Include in planned maintenance
   - Standard testing procedures

**Approval**: Standard PR review process

**Testing**: Full test suite

**Communication**: Include in quarterly security summary

### Response Escalation

If response deadlines cannot be met:

1. **Document Reason**: Create exception ticket with justification
2. **Get Approval**: Security Team Lead + Engineering Manager
3. **Implement Mitigation**: Apply temporary workarounds
4. **Set New Deadline**: Establish extended timeline with approval
5. **Add to Exception Log**: Document in vulnerability exception tracking

## Vulnerability Exception Process

Sometimes vulnerabilities cannot be immediately remediated. This section defines when and how to create exceptions.

### When to Create Exceptions

Exceptions are **ONLY** permitted when:

1. **False Positive**: Confirmed false positive after thorough investigation
2. **Inapplicable**: Vulnerability doesn't affect our platform or usage
3. **No Fix Available**: No patched version available from upstream
4. **Code Path Unused**: Vulnerable code path is provably not used
5. **Breaking Changes**: Update requires major refactoring (temporary only)
6. **Test Dependencies**: Vulnerability only affects development/test environment

### Exception Requirements

Every exception **MUST** include:

| Field | Description | Required | Example |
|-------|-------------|----------|---------|
| **Vulnerability ID** | CVE or advisory ID | Yes | CVE-2024-12345 |
| **Package** | Affected package name & version | Yes | numpy==1.24.0 |
| **Severity** | CRITICAL/HIGH/MEDIUM/LOW | Yes | MEDIUM |
| **Justification** | Detailed reason for exception | Yes | "Vulnerability only affects Windows; our deployment is Linux-only" |
| **Mitigation** | Compensating controls applied | Yes | "Network isolation prevents exploitation" |
| **Expiry Date** | When to reconsider | Yes | 2026-06-01 |
| **Owner** | Person responsible for review | Yes | jane.doe@example.com |
| **Review Ticket** | Tracking issue URL | Yes | https://github.com/org/repo/issues/123 |
| **Approved By** | Approver name & date | Yes | John Smith (2026-01-05) |

### Exception Expiry Guidelines

Maximum expiry periods by severity:

| Severity | Maximum Expiry | Recommended Expiry | Auto-Review Frequency |
|----------|---------------|-------------------|----------------------|
| **CRITICAL** | No exceptions allowed | N/A | N/A |
| **HIGH** | 30 days | 14 days | Weekly |
| **MEDIUM** | 90 days | 60 days | Monthly |
| **LOW** | 180 days | 90 days | Quarterly |

**Note**: CRITICAL vulnerabilities cannot be excepted - they must be fixed immediately or systems must be taken offline.

### Exception Creation Process

1. **Investigation** (Requires thorough analysis)
   ```bash
   # Verify vulnerability details
   pip-audit -r requirements.txt --desc --format json > vuln-details.json

   # Review CVE details and CVSS score
   # Check NVD, GitHub Advisories, vendor advisories

   # Analyze code paths
   # Verify if vulnerable code is actually used

   # Document findings in ticket
   ```

2. **Justification** (Create detailed documentation)
   - Document why vulnerability cannot be fixed immediately
   - Explain why it doesn't apply or is low risk
   - Describe any compensating controls
   - Provide evidence (screenshots, logs, analysis)

3. **Mitigation** (Apply compensating controls)
   - Network isolation
   - Input validation
   - Access controls
   - Monitoring and alerting
   - Workarounds

4. **Approval** (Get required sign-off)

   | Severity | Approver |
   |----------|----------|
   | HIGH | Security Team Lead + Engineering Manager |
   | MEDIUM | Development Team Lead |
   | LOW | Senior Developer + Code Review |

5. **Configuration** (Add to ignore files)

   **pip-audit (pyproject.toml)**:
   ```toml
   [tool.pip-audit]
   ignore-vulns = [
       # CVE-2024-12345: Windows-only, Linux deployment | Approved: J.Smith 2026-01-05 | Expires: 2026-06-01 | Review: GH-123
       "CVE-2024-12345",
   ]
   ```

   **Safety (.safety-policy.yml)**:
   ```yaml
   ignore:
     - id: "CVE-2024-12345"
       reason: "Vulnerability only affects Windows systems; deployment is Linux-only. Network isolation provides additional protection."
       expires: "2026-06-01"
       package: "example-package"
       version: "==1.2.3"
       approved_by: "John Smith (Security Team Lead)"
       approved_date: "2026-01-05"
       review_ticket: "https://github.com/org/repo/issues/123"
   ```

   **Trivy (.trivyignore)**:
   ```
   # CVE-2024-12345: Windows-only, Linux deployment | Approved: J.Smith 2026-01-05 | Expires: 2026-06-01 | Review: GH-123 | Package: example-package==1.2.3
   CVE-2024-12345
   ```

6. **Tracking** (Create monitoring)
   - Create calendar reminder for expiry date
   - Add to exception tracking spreadsheet
   - Set up automated expiry warnings
   - Schedule regular review meetings

### Exception Review Process

All exceptions are reviewed on a regular schedule:

**Weekly Review** (HIGH severity exceptions)
- Review all HIGH severity exceptions
- Check if patches are now available
- Verify compensating controls are effective
- Update expiry dates if needed
- Escalate if remediation is possible

**Monthly Review** (MEDIUM severity exceptions)
- Review all MEDIUM severity exceptions
- Check for new information or patches
- Update documentation
- Extend or remove exceptions

**Quarterly Review** (LOW severity exceptions)
- Review all LOW severity exceptions
- Clean up resolved exceptions
- Update policy based on trends
- Generate exception report for stakeholders

**Annual Review** (Policy review)
- Review exception process effectiveness
- Update approval workflows
- Revise expiry guidelines
- Train team on policy changes

### Exception Removal

Exceptions must be removed when:

1. **Fixed**: Patched version is available and deployed
2. **Expired**: Expiry date has passed
3. **No Longer Needed**: Package removed or replaced
4. **Risk Changed**: Severity increased or new exploits available

**Removal Process**:
```bash
# Remove from configuration files
# Edit pyproject.toml, .safety-policy.yml, .trivyignore

# Verify vulnerability is now detected
pip-audit -r requirements.txt
safety check --file requirements.txt
trivy fs .

# Either fix vulnerability or create new exception
# Commit changes with clear message

git add pyproject.toml .safety-policy.yml .trivyignore
git commit -m "security: remove expired exception for CVE-2024-12345

CVE-2024-12345 exception has expired. Vulnerability now fixed by
updating package from 1.2.3 to 1.2.4.

Refs: GH-123"
```

## Roles & Responsibilities

Clear ownership ensures accountability for dependency management:

| Role | Responsibilities |
|------|------------------|
| **Development Team** | - Perform monthly dependency updates<br>- Test updates thoroughly<br>- Create update PRs<br>- Respond to LOW/MEDIUM vulnerabilities<br>- Implement approved fixes |
| **Development Team Lead** | - Review and approve dependency updates<br>- Approve MEDIUM severity exceptions<br>- Coordinate major version updates<br>- Escalate blocking issues |
| **Security Team Lead** | - Review HIGH/CRITICAL vulnerabilities<br>- Approve HIGH severity exceptions<br>- Conduct security reviews<br>- Maintain security policies<br>- Oversee exception management |
| **Engineering Manager** | - Allocate resources for security work<br>- Approve HIGH severity exceptions (with Security Lead)<br>- Resolve priority conflicts<br>- Report to leadership on security posture |
| **CI/CD System** | - Run automated scans daily<br>- Scan every PR/push<br>- Generate scan artifacts<br>- Upload findings to GitHub Security tab<br>- Create GitHub issues for scheduled scan findings |
| **On-Call Engineer** | - Respond to CRITICAL vulnerability alerts<br>- Coordinate emergency patches<br>- Escalate to Security Team Lead<br>- Document incident response |

## Audit & Compliance

### Audit Trail Requirements

We maintain comprehensive audit trails for:

1. **Dependency Changes**
   - All changes committed to git with descriptive messages
   - PR reviews document rationale and testing
   - Lock files track exact versions and hashes

2. **Vulnerability Findings**
   - Scan results saved as workflow artifacts (90-day retention)
   - SARIF uploads to GitHub Security tab (permanent)
   - Exception documentation in configuration files

3. **Exception Management**
   - All exceptions documented in configuration files
   - Exception reviews tracked in GitHub issues
   - Approval records in git commit messages

4. **Incident Response**
   - CRITICAL/HIGH incidents documented in dedicated tickets
   - Post-mortem reports for major incidents
   - Timeline and actions recorded

### Compliance Reporting

We generate regular compliance reports:

| Report | Frequency | Audience | Content |
|--------|-----------|----------|---------|
| **Vulnerability Status** | Weekly | Development Team | Open vulnerabilities, exceptions, upcoming deadlines |
| **Security Summary** | Monthly | Engineering Leadership | Vulnerabilities addressed, exceptions granted, trends |
| **Dependency Health** | Monthly | Development Team | Outdated packages, update recommendations |
| **Exception Report** | Quarterly | Security Team + Leadership | All active exceptions, expiry dates, risk assessment |
| **Annual Security Review** | Yearly | Executive Leadership | Year-over-year trends, policy effectiveness, recommendations |

### Metrics & KPIs

We track the following metrics:

- **Mean Time to Remediate (MTTR)** by severity
- **Vulnerability Backlog**: Open vulnerabilities by severity
- **Exception Count**: Active exceptions by severity
- **Dependency Freshness**: Age of dependencies vs. latest versions
- **Update Frequency**: Actual vs. scheduled updates
- **Scan Coverage**: Percentage of dependencies scanned
- **False Positive Rate**: Scanner accuracy

Target KPIs:
- CRITICAL MTTR: < 24 hours
- HIGH MTTR: < 7 days
- MEDIUM MTTR: < 30 days
- Exception Count: < 5 active exceptions
- Dependency Age: < 6 months behind latest stable

## Policy Review & Updates

This policy is a living document that evolves with our practices:

**Review Schedule**:
- **Quarterly**: Minor updates, metric review, process improvements
- **Annually**: Major revision, effectiveness assessment
- **Ad-Hoc**: After major incidents or significant process changes

**Update Process**:
1. Propose changes via GitHub issue
2. Discuss with Development Team + Security Team
3. Get approval from Engineering Manager
4. Update document with version number and date
5. Communicate changes to all stakeholders
6. Conduct training if significant changes

**Change Log**:

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-05 | Auto-Claude | Initial policy creation |

## Related Documentation

- [SECURITY.md](../SECURITY.md) - Public-facing security policy and vulnerability reporting
- [SECURITY_SCANNING.md](SECURITY_SCANNING.md) - Technical scanner configuration and usage
- [CI Workflow](../.github/workflows/ci.yml) - Automated security scanning implementation
- [Scheduled Scans](../.github/workflows/scheduled-vulnerability-scan.yml) - Daily monitoring workflow

## Contact & Support

For questions about this policy:

- **General Questions**: Create issue with [Policy] tag
- **Exception Requests**: Create issue with [Security Exception] template
- **Security Concerns**: Email security@example.com
- **Emergency**: Contact on-call engineer via PagerDuty/Slack

---

**Document Version**: 1.0
**Last Updated**: 2026-01-05
**Next Review**: 2026-04-05 (Quarterly)
**Owner**: Security Team Lead
**Approved By**: Engineering Manager
