# GitHub Token Authentication Fix

## Problem
Currently getting `HTTP 403 - Resource not accessible by integration` when trying to push to your repositories. This means the current GitHub token lacks write permissions.

## Root Cause
The current `GITHUB_TOKEN` environment variable is set to a Codespaces-generated token which has **read-only** access to your public repos but **no write access** to push commits.

## Solution: Create a Personal Access Token

### Step 1: Generate New Token
1. Go to: https://github.com/settings/tokens/new
2. Or: Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token

### Step 2: Select Required Scopes
Check these scopes:
- ✅ **repo** - Full control of private repositories
  - Includes: public_repo, repo, write:repo_hook, delete_repo
- ✅ **gist** - Create gists (optional)

### Step 3: Copy and Store Token
- Click "Generate token"
- **COPY THE TOKEN IMMEDIATELY** (you can't see it again)
- Save it somewhere safe

### Step 4: Update Your Authentication

#### Option A: Interactive Login (Recommended)
```bash
gh auth logout
gh auth login --scopes repo --web
# Browser will open, authenticate, copy the token code shown
```

#### Option B: Direct Token Input
```bash
echo "PASTE_YOUR_TOKEN_HERE" | gh auth login --with-token
```

#### Option C: Set as Environment Variable
```bash
export GITHUB_TOKEN="your_personal_access_token"
# Test it
gh auth status
```

### Step 5: Verify It Works
```bash
gh api user
# Should show your user info without errors
```

## After Authentication Fix

Once you have the proper token, the empty repo population will work:

```bash
# Option 1: Use the gh api approach (creates files directly)
bash /workspaces/FUDMA-BOT/scripts/GITHUB_UNWRAPPED_FIX_GUIDE.sh

# Option 2: Use git push (now that token has write access)
cd /tmp/CDK-predictive-model-AI && git push -u origin main
```

## What Each Token Type Allows

| Token Type | Read Own Repos | Write Own Repos | Read Public | 
|-----------|---|---|---|
| Codespaces Default | ✅ | ❌ | ✅ |
| Personal Access (repo) | ✅ | ✅ | ✅ |
| Personal Access (no scope) | ❌ | ❌ | ❌ |
| Personal Access (gist) | ❌ | ❌ | ❌ |

## Estimated Time to Fix
- Creating token: 1 minute
- Updating authentication: 2 minutes
- Re-running population script: 5 minutes
- **Total: ~8 minutes**

## Support
If you continue getting 403 errors after this, check:
1. `gh auth status` - verify token is active
2. `gh api user` - verify token has access to API
3. `gh repo view SagsMan/CDK-predictive-model-AI` - verify you own the repo
