# PyPI Publishing Setup Checklist

Complete these steps in order to set up automated PyPI publishing for obi.

## Prerequisites
- [ ] GitHub account with access to `obinexusmk2/obi` repository
- [ ] PyPI account (or ability to create one)
- [ ] Local git setup with push access

## Phase 1: PyPI Configuration (5 minutes)

- [ ] **Step 1.1**: Create PyPI account at https://pypi.org/account/register/
- [ ] **Step 1.2**: Verify PyPI email address
- [ ] **Step 1.3**: Go to https://pypi.org/manage/account/ → API tokens
- [ ] **Step 1.4**: Create API token named `obi-gh-actions`
- [ ] **Step 1.5**: Copy token (starts with `pypi-`)
- [ ] **Step 1.6**: Paste token in safe location (you'll need it in Phase 2)

## Phase 2: GitHub Configuration (5 minutes)

- [ ] **Step 2.1**: Go to GitHub repository settings
- [ ] **Step 2.2**: Create environment named `pypi` (Settings → Environments)
- [ ] **Step 2.3**: Add secret `PYPI_API_TOKEN` (Settings → Secrets and variables → Actions)
- [ ] **Step 2.4**: Paste the PyPI token from Phase 1
- [ ] **Step 2.5**: Verify workflow file exists: `.github/workflows/publish.yml`

## Phase 3: Repository Preparation (5 minutes)

- [ ] **Step 3.1**: Verify `obi/pyproject.toml` exists and is valid
- [ ] **Step 3.2**: Update version in `obi/pyproject.toml` (e.g., `0.1.0`)
- [ ] **Step 3.3**: Create or update `CHANGELOG.md` with release notes
- [ ] **Step 3.4**: Commit changes: `git commit -m "chore: prepare for PyPI"`
- [ ] **Step 3.5**: Push to main: `git push origin main`

## Phase 4: Workflow Test (Optional, 2-5 minutes)

- [ ] **Step 4.1**: Go to GitHub Actions tab
- [ ] **Step 4.2**: Find "Publish to PyPI" workflow
- [ ] **Step 4.3**: Click "Run workflow" → Select `main` branch
- [ ] **Step 4.4**: Monitor the build (watch for errors)
- [ ] **Step 4.5**: Check that all steps pass ✓

## Phase 5: First Release (2 minutes)

Choose ONE option:

### Option A: Automatic Publishing (On Push)
- [ ] **Step 5A.1**: Make code changes on `main` branch
- [ ] **Step 5A.2**: Push to main: `git push origin main`
- [ ] **Step 5A.3**: Workflow triggers automatically ✓

### Option B: Tag-Based Release (Recommended)
- [ ] **Step 5B.1**: Create tag: `git tag -a v0.1.0 -m "Release 0.1.0"`
- [ ] **Step 5B.2**: Push tag: `git push origin v0.1.0`
- [ ] **Step 5B.3**: Workflow triggers automatically ✓

## Phase 6: Verification (1 minute)

- [ ] **Step 6.1**: Check GitHub Actions for successful run ✓
- [ ] **Step 6.2**: Visit https://pypi.org/project/obi/
- [ ] **Step 6.3**: Verify package appears with correct version
- [ ] **Step 6.4**: Test installation: `pip install obi==0.1.0`

---

## Workflow Status

| Phase | Status | Notes |
|-------|--------|-------|
| 1. PyPI Setup | ⏳ TODO | |
| 2. GitHub Config | ⏳ TODO | |
| 3. Repo Prep | ⏳ TODO | |
| 4. Test Workflow | ⏳ TODO | |
| 5. First Release | ⏳ TODO | |
| 6. Verify | ⏳ TODO | |

**Mark items as `✓ DONE` as you complete them.**

---

## Files Created/Modified

| File | Status | Purpose |
|------|--------|---------|
| `.github/workflows/publish.yml` | ✓ Created | GitHub Actions workflow |
| `obi/pyproject.toml` | ✓ Exists | Package configuration |
| `CHANGELOG.md` | ⏳ Create | Release notes |
| `PYPI_PUBLISHING_GUIDE.md` | ✓ Created | Detailed guide (this repo) |

---

## Quick Reference Commands

```bash
# Clone your repository
git clone https://github.com/obinexusmk2/obi.git
cd obi

# Update version (edit file)
vim obi/pyproject.toml

# Commit changes
git add obi/pyproject.toml CHANGELOG.md
git commit -m "chore: prepare for PyPI release"
git push origin main

# Create a release tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# Check package locally (after publishing)
pip install obi==0.1.0
```

---

## Common Issues & Solutions

| Issue | Solution | Doc Reference |
|-------|----------|---|
| PyPI token not working | Create new token, update GitHub secret | PYPI_PUBLISHING_GUIDE.md → Step 1 |
| Workflow doesn't trigger | Check branch is `main` or `release` | PYPI_PUBLISHING_GUIDE.md → Troubleshooting |
| Package name taken | Choose different name, update pyproject.toml | PYPI_PUBLISHING_GUIDE.md → Troubleshooting |
| Build fails | Check logs in GitHub Actions tab | PYPI_PUBLISHING_GUIDE.md → Troubleshooting |

---

## Next Steps After Setup

Once publishing is working:

1. **Automate version bumping** (optional)
   - Use [bump2version](https://github.com/c17r/bump2version)
   - Automatically update version on release

2. **Set up PyPI TestPyPI** (optional)
   - Test publishing to TestPyPI first
   - Add separate workflow for staging releases

3. **Add release notes** 
   - Create detailed GitHub Releases
   - Link to CHANGELOG.md

4. **Monitor package health**
   - Check PyPI stats
   - Review download metrics
   - Monitor for security issues

---

**Last Updated**: 2026-05-15  
**Workflow File**: `.github/workflows/publish.yml`  
**For Questions**: See PYPI_PUBLISHING_GUIDE.md
