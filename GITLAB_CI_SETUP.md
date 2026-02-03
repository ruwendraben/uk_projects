# GitLab CI/CD Setup Instructions

## Prerequisites
- GitLab account and project created
- Git installed on your machine

## Step 1: Initialize and Push Repository

```bash
cd E:\Ruwen\workspace\abc_company\abc_data_analytics

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Phase 1+2 complete: Onboarding + Data Source Exploration + GitLab CI"

# Add remote (replace with your GitLab project URL)
git remote add origin https://gitlab.com/your-company/abc-data-analytics.git

# Push to main branch
git push -u origin main
```

## Step 2: Configure GitLab CI Variables

Go to your GitLab project → Settings → CI/CD → Variables

Add these variables:

### For Docker Registry (optional)
- `CI_REGISTRY_USER`: Your GitLab username
- `CI_REGISTRY_PASSWORD`: Your GitLab personal access token

### For AWS Deployment (optional - when ready to deploy)
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_ACCOUNT_ID`: Your AWS account ID

## Step 3: Configure Merge Request Approvals

Go to Settings → Merge requests → Approval rules

Add these approval requirements:
1. **QA Team**: Approve test coverage > 80%
2. **AppSec Team**: Approve security scan (bandit + safety)
3. **Tech Lead**: Final approval before merge

## Step 4: Set Protected Branches

Go to Settings → Repository → Protected branches

Protect `main` branch:
- Require approvals from QA
- Require approvals from AppSec
- Require approvals from Tech Lead
- Dismiss stale approvals on push

## Pipeline Flow

### On Merge Request:
1. **Test Stage** (automatic)
   - Runs unit tests
   - Generates coverage report
   - Fails if coverage < 80%

2. **Security Stage** (automatic)
   - Bandit security scan
   - Safety dependency check
   - Secret detection

### On Main Branch (after approval):
3. **Build Stage** (manual trigger)
   - Build Docker image
   - Push to registry

4. **Deploy Stages** (manual trigger)
   - Deploy to staging
   - Deploy to production (requires staging success)

## Team Role Definitions

### QA Team
- Reviews test coverage reports
- Runs manual integration tests
- Approves when coverage > 80% and tests pass

### AppSec Team
- Reviews bandit SAST reports
- Reviews safety vulnerability check
- Approves when no critical/high vulnerabilities

### Tech Lead
- Approves code quality
- Reviews architecture
- Approves merge to main
- Triggers build and deploy

## Testing Locally Before Push

```bash
cd django_webserver

# Run unit tests
python manage.py test main

# Check coverage
pip install coverage
coverage run --source='main' manage.py test main
coverage report

# Run security scans
pip install bandit safety
bandit -r main
safety check
```

## Troubleshooting

If CI fails:
1. Check pipeline logs: Project → CI/CD → Pipelines
2. View job logs for details
3. Fix and push new commit (CI re-runs)
4. Approvals reset on new push (if `dismiss_stale_approvals` enabled)
