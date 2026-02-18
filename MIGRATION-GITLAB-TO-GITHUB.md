# Migrating from GitLab to GitHub

This project’s CI is set up for **GitHub Actions** (see `.github/workflows/ci.yml`). You can move the repo to GitHub and keep the same pipeline behavior.

## What’s already done

- **`.github/workflows/ci.yml`** – workflow that mirrors your GitLab pipeline:
  - **Test** – unit tests + coverage (Cobertura) on every push/PR to `main`
  - **Security** – Bandit, Safety, detect-secrets (allowed to fail)
  - **Build** – Docker build & push to **GitHub Container Registry** (manual)
  - **Deploy** – staging and production (manual, same order as GitLab)

## Steps to migrate

### 1. Create a GitHub repo

- On GitHub: **New repository** (same or new name).
- Do **not** add a README if you already have one locally.

### 2. Point this repo at GitHub

```bash
# Add GitHub as a new remote (replace with your GitHub repo URL)
git remote add github https://github.com/YOUR_ORG/abc_data_analytics.git

# Or replace origin if you’re fully moving off GitLab
# git remote set-url origin https://github.com/YOUR_ORG/abc_data_analytics.git
```

### 3. Push to GitHub

```bash
git push -u github main
# or: git push -u origin main
```

### 4. Optional: manual build & deploy

Manual steps (like GitLab’s “play” button) are done via **Run workflow** in GitHub Actions:

1. **Actions** → select **CI** → **Run workflow**.
2. Choose branch (e.g. `main`).
3. Check what you want:
   - **Build and push Docker image** – builds and pushes to GHCR.
   - **Deploy to staging** – runs staging deploy.
   - **Deploy to production** – runs after staging (same as GitLab).

### 5. Environments (for deploy jobs)

The workflow uses GitHub **environments** `staging` and `production` (for logs and optional approvals):

- **Settings** → **Environments** → create **staging** and **production**.
- Optionally add required reviewers on **production** so deploys need approval.

### 6. Docker images (GHCR instead of GitLab Registry)

- Images are pushed to **GitHub Container Registry**:  
  `ghcr.io/<org>/<repo>:<sha>` and `ghcr.io/<org>/<repo>:latest`.
- No extra secrets are needed; `GITHUB_TOKEN` is used automatically.
- To pull from GHCR elsewhere, use a **Personal Access Token (classic)** with `read:packages` and log in to `ghcr.io`.

### 7. Detect-secrets baseline (optional)

If you use `detect-secrets` and don’t have a baseline yet:

```bash
pip install detect-secrets
detect-secrets scan > .secrets.baseline
# Edit .secrets.baseline to allow known false positives, then commit.
```

If you don’t use it, you can remove the `security-secrets` job from `.github/workflows/ci.yml`.

---

After this, you can run everything on GitHub and, when ready, remove or archive the GitLab project.
