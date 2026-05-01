# Resolve Merge Conflicts

Intelligently resolve merge conflicts in a branch before merging to main.

## Instructions

You are resolving merge conflicts for a feature branch that's ready to merge but has conflicts with main. Analyze each conflicted file and apply the appropriate resolution strategy.

## Conflict Resolution Strategies

### 1. Tracking/Metrics Files (Combine Both)

**Files**: `app_docs/agentic_kpis.md`

- **Strategy**: Keep BOTH entries, merge tables
- **Reason**: Each ADW run adds its own row, both are valid
- **Action**:
  - Combine summary metrics (use max for streaks, sum for totals)
  - Append all rows in the KPIs table
  - Sort by date descending

### 2. Auto-generated Files (Regenerate)

**Files**: `public/sw.js`, `.next/**`

- **Strategy**: Delete and regenerate
- **Reason**: Build artifacts, should be regenerated
- **Action**:
  - Take incoming (main) version
  - Run build to regenerate if needed
  - Or mark for rebuild in next build

### 3. Configuration Files (Intelligent Merge)

**Files**: `.mcp.json`, `playwright-mcp-config.json`, `.github/workflows/**`

- **Strategy**: Merge configurations intelligently
- **Reason**: Both branches may add valid config
- **Action**:
  - For JSON: Parse both, merge objects/arrays
  - For YAML: Merge keys, keep unique values
  - Validate after merge

### 4. Documentation Files (Prefer Newest)

**Files**: `.claude/commands/**`, `app_docs/**`, `README.md`

- **Strategy**: Take most recent or combine sections
- **Reason**: Documentation updates, usually additive
- **Action**:
  - If entirely different sections: combine both
  - If same section updated: take incoming (main)
  - Review for completeness

### 5. Source Code (Manual Review Required)

**Files**: `src/**`, `tests/**`

- **Strategy**: Require human review
- **Reason**: Logic changes, risk of breaking functionality
- **Action**:
  - Flag for manual resolution
  - Provide context about both changes
  - Suggest which might take precedence

## Resolution Process

1. **Analyze Conflicts**

   ```bash
   git merge main --no-commit
   git diff --name-only --diff-filter=U
   ```

2. **For Each Conflicted File**
   - Identify file type and category
   - Apply appropriate strategy
   - Resolve conflict
   - Stage resolved file

3. **Validate Resolution**
   - Run linters
   - Run tests
   - Verify build succeeds

4. **Complete Merge**
   ```bash
   git add .
   git commit -m "chore: resolve merge conflicts with main"
   ```

## Example Resolutions

### KPI File Merge

```markdown
# Before (conflict)

<<<<<<< HEAD
| 2026-02-12 | e0066ae3 | 6 | /bug | 1 | 93 | 861/440/17 |
=======
| 2026-02-12 | 974f08ca | 7 | /bug | 1 | 118 | 351/7/9 |

> > > > > > > main

# After (resolved)

| 2026-02-12 | 974f08ca | 7 | /bug | 1 | 118 | 351/7/9 |
| 2026-02-12 | e0066ae3 | 6 | /bug | 1 | 93 | 861/440/17 |
```

### JSON Config Merge

```json
// Before (conflict)
<<<<<<< HEAD
{ "servers": { "playwright": { "port": 9000 } } }
=======
{ "servers": { "ide": { "port": 8000 } } }
>>>>>>> main

// After (resolved)
{
  "servers": {
    "playwright": { "port": 9000 },
    "ide": { "port": 8000 }
  }
}
```

## Guidelines

- **Be Conservative**: When in doubt, prefer main's version
- **Preserve Intent**: Keep the purpose of both changes when possible
- **Document Decisions**: Add comments explaining non-obvious resolutions
- **Test Thoroughly**: Always validate after resolution

## Output Format

Provide a summary of:

1. Total conflicts found
2. Resolution strategy used for each file
3. Any manual review required
4. Validation results (lint, test, build)
