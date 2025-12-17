# Codespace Recovery Mode - Error Analysis & Fixes

**Date:** December 17, 2025  
**Log Source:** `~/.vscode-remote/data/logs/20251217T052016/exthost1/remoteexthost.log`  
**Status:** 9 critical errors identified causing recovery mode

---

## 🔴 Critical Errors Found

### 1. **File Lock Collision (HIGHEST PRIORITY)**
```
Error: EEXIST: file already exists, open '/home/vscode/.vscode-remote/data/User/workspaceStorage/-3847feb/vscode.lock'
Severity: CRITICAL
Impact: Prevents workspace from initializing correctly
```
**Root Cause:** The `.vscode-remote` directory has a stale or conflicting lock file from a previous codespace session.

**Fix:**
```bash
# Clean the lock file (this resets the workspace state)
rm -rf ~/.vscode-remote/data/User/workspaceStorage/*/vscode.lock

# OR completely reset VS Code remote state (nuclear option)
rm -rf ~/.vscode-remote/data/User/workspaceStorage/
```

---

### 2. **Navigator API Migration Error (7x occurrences)**
```
Error: PendingMigrationError: navigator is now a global in nodejs
Reference: https://aka.ms/vscode-extensions/navigator
Severity: HIGH
Count: 7 errors across extension loading
```
**Root Cause:** Multiple extensions are using the deprecated Node.js `navigator` API pattern. This typically affects:
- Older Prettier versions
- ESLint plugin extensions
- Code linting extensions

**Fix Options:**

**Option A: Update Extensions to Latest Versions**
Update `.devcontainer/devcontainer.json`:
```jsonc
"esbenp.prettier-vscode": "latest"  // Currently: 11.0.2 (update available)
```

**Option B: Disable Problematic Extensions**
Temporarily disable extensions in `.devcontainer/devcontainer.json`:
```jsonc
"extensions": [
  // Remove or comment out:
  // "esbenp.prettier-vscode",  // Known navigator API issues
  // "ms-eslint.eslint"         // May have compatibility issues
]
```

---

### 3. **Copilot Chat Configuration Error**
```
Error: chatParticipant must be declared in package.json: claude-code
Severity: HIGH
Impact: Copilot Chat extension fails to load
```
**Root Cause:** The `claude-code` chat participant is registered by Copilot Chat but not properly declared in the extension's `package.json` manifest, or conflicts with custom agent definitions.

**Fix:**
```bash
# Option 1: Disable Copilot Chat extension (recommended for stability)
# Edit .devcontainer/devcontainer.json:
"extensions": [
  // Remove if codespace stability is critical:
  // "GitHub.copilot-chat",
  "GitHub.copilot"  // Keep Copilot core, just remove chat
]

# Option 2: Clear Copilot Chat cache and reset
rm -rf ~/.vscode-remote/extensions/github.copilot-chat-*/
```

---

### 4. **Unknown Agent Registration Error**
```
Error: Unknown agent: "copilot-swe-agent"
Severity: MEDIUM
Impact: SWE agent features not available, but doesn't block codespace
```
**Root Cause:** A custom or experimental agent ("copilot-swe-agent") is referenced but not registered in the system.

**Fix:**
```bash
# Check what agents are trying to register:
grep -r "copilot-swe-agent" ~/.vscode-remote/

# If no matches, this is a false agent reference. Delete extension cache:
rm -rf ~/.vscode-remote/extensions/
```

---

### 5. **File Watcher Crashes (2x occurrences)**
```
Warning: [File Watcher (node.js)] Watcher shutdown because watched path got deleted
Timestamp: 06:10:25.150, 06:12:33.322
Severity: MEDIUM
Impact: File watching temporarily disabled (recovery usually succeeds)
```
**Root Cause:** The Node.js file watcher detected that a monitored directory was deleted while watching it (likely during cleanup or file operations).

**Fix:**
```bash
# Ensure no background processes are deleting watched directories:
ps aux | grep -E "(python|node|npm)" | grep -v grep

# If Python tests are running, kill them:
pkill -f pytest
pkill -f node
```

---

## 📋 Recommended Action Plan

### **Immediate (Quick Fix - 2 minutes):**

```bash
cd /workspaces/TeamAI

# 1. Clear all lock files
rm -rf ~/.vscode-remote/data/User/workspaceStorage/*/vscode.lock

# 2. Clear Copilot Chat cache
rm -rf ~/.vscode-remote/extensions/github.copilot-chat-*/

# 3. Kill any lingering processes
pkill -f pytest 2>/dev/null || true
pkill -f "python.*test" 2>/dev/null || true

# 4. Refresh the codespace (don't reload yet - do this step-by-step)
```

---

### **Short-term (Better Stability - 5 minutes):**

Update `.devcontainer/devcontainer.json` to disable problematic extensions:

```jsonc
"extensions": [
  "ms-python.python",
  "ms-python.vscode-pylance",
  "ms-python.black-formatter",
  "ms-python.pylint",
  "ms-azuretools.vscode-docker",
  "GitHub.copilot",
  // REMOVE THESE FOR STABILITY:
  // "GitHub.copilot-chat",           // ← Causing chatParticipant errors
  "eamodio.gitlens",
  "streetsidesoftware.code-spell-checker",
  "ms-vscode.makefile-tools",
  "redhat.vscode-yaml",
  // "esbenp.prettier-vscode"        // ← Causing navigator API errors (optional)
]
```

After editing, rebuild the container:
```bash
# In VS Code Command Palette: "Dev Containers: Rebuild Container"
# OR from terminal:
# Close VS Code, then: git push, then reopen codespace
```

---

### **Long-term (Production Stability - done later):**

1. **Update all extensions to latest versions**
   - Check Azure CLI, Prettier, ESLint versions
   - Remove unsupported extensions

2. **Implement postCreateCommand cleanup**
   ```jsonc
   "postCreateCommand": "rm -rf ~/.vscode-remote/data/User/workspaceStorage/*/vscode.lock && pip install -r backend/requirements.txt && cd backend && alembic upgrade head || true",
   ```

3. **Add health check script**
   ```bash
   #!/bin/bash
   # .devcontainer/health-check.sh
   pkill -f "test.*pytest" 2>/dev/null || true
   pkill -f "node.*ts-node" 2>/dev/null || true
   echo "✓ Codespace cleaned"
   ```

---

## 📊 Error Summary Table

| Error | Severity | Fix | Action |
|-------|----------|-----|--------|
| Lock file collision | 🔴 CRITICAL | Clear `vscode.lock` | Do immediately |
| Navigator API (7x) | 🟠 HIGH | Disable extensions or update | Update `.devcontainer.json` |
| Copilot Chat particle | 🟠 HIGH | Disable `GitHub.copilot-chat` | Update `.devcontainer.json` |
| Unknown SWE agent | 🟡 MEDIUM | Delete extension cache | Optional cleanup |
| File watcher crashes | 🟡 MEDIUM | Kill background processes | Ongoing monitoring |

---

## ✅ Verification

After applying fixes, run:
```bash
# Check for remaining errors
cat ~/.vscode-remote/data/logs/*/exthost1/remoteexthost.log | grep "\[error\]" | wc -l
# Expected: Should drop from 9 to 0-1

# Monitor file watcher
cat ~/.vscode-remote/data/logs/*/remoteagent.log | grep "Watcher shutdown" | wc -l
# Expected: Should not increase
```

---

## 🎯 Next Steps

1. **Apply Immediate Fix** (clear lock files)
2. **Update `.devcontainer.json`** (disable problematic extensions)
3. **Rebuild Container** (VS Code: "Dev Containers: Rebuild Container")
4. **Monitor Logs** (check for errors in first 5 minutes after restart)
5. **Document Success** (update this file with results)
