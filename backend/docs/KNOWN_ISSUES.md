# Known Issues

## Non-Blocking

### 1. In-Memory Storage
**Severity**: Low
**Description**: Index repository and memory stores use in-memory dictionaries. Data is lost on server restart.
**Resolution**: Stage 2 will add persistent storage (SQLite/PostgreSQL).

### 2. Rule-Based Planner
**Severity**: Low
**Description**: The agent planner uses simple pattern matching (`read`, `terminal`, `write` prefixes) instead of LLM-powered planning.
**Resolution**: Stage 3 will replace with LLM-powered planner.

### 3. Ollama Availability Not Checked at Startup
**Severity**: Low
**Description**: The LLM engine does not verify Ollama is running during startup. LLM calls will fail at runtime if Ollama is not available.
**Resolution**: By design — Ollama is optional for Stage 1 since no endpoints use LLM yet.

### 4. OpenAI Provider Not Implemented
**Severity**: Low
**Description**: OpenAI provider raises `LLMProviderError` on generate calls.
**Resolution**: Stage 3 implementation planned.

### 5. No Authentication
**Severity**: Medium (for production)
**Description**: All API endpoints are publicly accessible without authentication.
**Resolution**: Stage 7 will add auth middleware.

### 6. Terminal Tool Uses shell=True
**Severity**: Medium (security)
**Description**: Terminal tool executes commands with `shell=True`, which can be a security risk in production.
**Resolution**: Stage 4 will add sandboxed execution environment.

### 7. No Input Path Sanitization
**Severity**: Medium (security)
**Description**: File and write tools accept any path without restricting to workspace boundaries.
**Resolution**: Stage 2 will add workspace-scoped path validation.

## Resolved in Stage 1

| Issue | Resolution |
|-------|-----------|
| Broken imports in main.py | Fixed — uses core/app.py factory |
| Broken imports in executor.py | Fixed — uses engines.agent and engines.tools |
| Missing `__init__.py` files | Fixed — 22 packages now valid |
| Duplicate package nesting | Fixed — flat engine structure |
| Missing executor route | Fixed — POST /executor/run added |
| No logging | Fixed — structured logging with file output |
| Route validation failing at startup | Fixed — uses OpenAPI schema paths |
| Monolithic parser | Fixed — split into 4 analyzers |
