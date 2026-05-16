# PyPI Publishing Setup Guide for obi

This guide walks you through setting up automated PyPI publishing for the **obi** package using GitHub Actions.

## Overview

The publishing workflow (`.github/workflows/publish.yml`) is configured to:
- **Trigger** on pushes to `main` or `release` branches
- **Build** the package across Linux, Windows, and macOS
- **Test** the package before publishing
- **Publish** to PyPI using a secure API token
- **Create releases** for tagged versions

## Step 1: Create a PyPI Account and API Token

### If you don't have a PyPI account:
1. Go to [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. Create an account with your email
3. Verify your email address

### Create an API Token:
1. Log in to PyPI at [https://pypi.org/manage/account/](https://pypi.org/manage/account/)
2. Go to **Account settings** → **API tokens**
3. Click **Add API token**
4. Name it: `obi-gh-actions` (or similar)
5. Scope: Select **Entire account** (or specific project if you have it on PyPI already)
6. Click **Create token**
7. **Copy the token** (you'll only see it once!)
   - Token format: `pypi-AgEIc...` (starts with `pypi-`)

**⚠️ KEEP THIS TOKEN SECRET!** Never commit it to your repository.

---

## Step 2: Reserve the PyPI Package Name

1. Go to [https://pypi.org/project/obi/](https://pypi.org/project/obi/)
2. If the package doesn't exist, you don't need to do anything—it will be created on first publish
3. If it exists and is owned by someone else, contact them or choose a different name

---

## Step 3: Configure GitHub Repository Settings

### 3a: Create a GitHub Environment (Recommended)

1. Go to your GitHub repository: `https://github.com/obinexusmk2/obi`
2. Click **Settings** → **Environments**
3. Click **New environment**
4. Name it: `pypi` (matches the workflow)
5. Click **Configure environment**

### 3b: Add the PyPI Token as a Repository Secret

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `PYPI_API_TOKEN`
4. Value: Paste the token you created in Step 1
5. Click **Add secret**

### 3c: (Optional) Add Environment Protection Rules

For extra security with the `pypi` environment:
1. In the environment settings, scroll to **Deployment branches**
2. Select **Protected branches** to only allow deployments from protected branches
3. Or select specific branches like `main` and `release`

---

## Step 4: Verify Your Repository Structure

Ensure your repository has this structure:

```
obi/
├── .github/
│   └── workflows/
│       └── publish.yml          ← Created automatically
├── obi/
│   ├── __init__.py
│   ├── pyproject.toml           ← Already exists
│   ├── README.md
│   ├── bindings/
│   ├── core/
│   ├── drivers/
│   ├── sdk/
│   └── tests/
├── .gitignore
└── README.md
```

---

## Step 5: Prepare Your First Release

### Update the Version Number

In `obi/pyproject.toml`, update the version:

```toml
[project]
name = "obi"
version = "0.1.0"              # ← Change from "0.1.0-alpha"
```

Use semantic versioning: `MAJOR.MINOR.PATCH` (e.g., `0.1.0`, `1.0.0`)

### Update CHANGELOG (Recommended)

Create a `CHANGELOG.md` file documenting your releases:

```markdown
# Changelog

## [0.1.0] - 2026-05-15

### Added
- Initial PyPI release
- Core SDK functionality
- Python 3.9-3.12 support

### Changed
- Moved from pre-release to stable alpha

### Fixed
- Cython compilation issues on Windows
```

### Commit Your Changes

```bash
cd /path/to/obi
git add obi/pyproject.toml CHANGELOG.md .github/workflows/publish.yml
git commit -m "chore: prepare for PyPI publishing"
git push origin main
```

---

## Step 6: Test the Workflow (Optional but Recommended)

### Manual Workflow Trigger

1. Go to your GitHub repository
2. Click **Actions** tab
3. Find **Publish to PyPI** workflow
4. Click **Run workflow**
5. Select branch: `main`
6. Click **Run workflow**

Monitor the workflow run to check for errors before publishing.

### What to Check For:

- ✅ All build steps complete successfully
- ✅ Tests pass on all Python versions
- ✅ Twine package check passes (warnings are OK)
- ❌ No authentication errors with PyPI

---

## Step 7: Publish Your First Release

### Option A: Push to `main` Branch (Automatic)

```bash
git push origin main
```

The workflow will automatically trigger and publish to PyPI.

### Option B: Create a Git Tag (Recommended for Releases)

```bash
# Tag your release
git tag -a v0.1.0 -m "Release version 0.1.0"

# Push the tag
git push origin v0.1.0
```

This creates a GitHub Release and publishes to PyPI.

---

## Step 8: Verify Publication

After the workflow completes:

1. Check **GitHub Actions** tab for successful run
2. Visit [https://pypi.org/project/obi/](https://pypi.org/project/obi/)
3. Verify your package appears with the correct version
4. Test installation:
   ```bash
   pip install obi==0.1.0
   ```

---

## Troubleshooting

### "Permission denied" Error During Publish

**Cause**: Invalid or expired PyPI token

**Solution**:
1. Create a new token on PyPI
2. Update the `PYPI_API_TOKEN` secret in GitHub
3. Re-run the workflow

### "Project name ... already exists" Error

**Cause**: Someone else owns the package name on PyPI

**Solution**:
1. Choose a different package name (e.g., `obi-nnamdi`)
2. Update `name` in `obi/pyproject.toml`
3. Update the workflow (if needed)

### "twine check" Fails

**Cause**: Invalid metadata in `pyproject.toml`

**Solution**:
1. Check your `README.md` file exists and is valid reStructuredText
2. Verify all required fields in `[project]` section
3. Test locally: `python -m twine check dist/*`

### Build Fails on Windows/macOS

**Cause**: Missing Cython compilation dependencies

**Solution**:
1. Ensure `cmake` is in your build requirements ✓ (already in pyproject.toml)
2. Check for platform-specific syntax errors in `.pyx` files
3. Run locally on the failing platform to debug

### Workflow Doesn't Trigger

**Cause**: Branch doesn't match or paths excluded

**Solution**:
1. Verify you pushed to `main` or `release` branch
2. Check that changes are in `obi/` directory or `.github/workflows/`
3. Manually trigger via **Actions** → **Run workflow**

---

## Ongoing Maintenance

### For Each New Release:

1. **Update version** in `obi/pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Commit and push** to `main` or `release`
4. **Create a git tag**: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
5. **Push the tag**: `git push origin vX.Y.Z`

### Automate Version Bumping (Optional):

Consider using [bump2version](https://github.com/c17r/bump2version) or [python-semantic-release](https://github.com/relekang/python-semantic-release) to automate version updates.

---

## Security Best Practices

- ✅ Use API tokens, not passwords
- ✅ Use GitHub Environments for production publishing
- ✅ Limit token scope to the project if possible
- ✅ Rotate tokens periodically (every 6-12 months)
- ✅ Never hardcode tokens in workflow files
- ✅ Use `secrets.PYPI_API_TOKEN` as shown

---

## Additional Resources

- [PyPI Documentation](https://pypi.org)
- [Python Packaging Guide](https://packaging.python.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)

---

## Questions or Issues?

If you encounter problems:
1. Check the **Actions** tab for detailed error messages
2. Review logs for each failed step
3. Check PyPI account for publishing history
4. Verify `pyproject.toml` syntax with: `python -m tomli obi/pyproject.toml`
