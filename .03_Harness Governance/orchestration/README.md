# Orchestration Scaffolds

This folder contains implementation-ready orchestration assets referenced by the PDR automation docs.

## n8n

- Workflow JSON: `orchestration/n8n/pdr-zip-intake-phase1.workflow.json`
- Import this file into n8n and set environment variable `CHROMATIC_WEBHOOK_SECRET`.
- Validator: `orchestration/n8n/validate_workflow.py`
- Import runner: `orchestration/n8n/import_workflow.py`
- Trigger endpoint path: `/webhook/pdr-zip-intake-phase1`

Expected local bridge command:

```powershell
python .01_PDRs/pdr_zip_ingest.py watch --webhook-url "http://localhost:5678/webhook/pdr-zip-intake-phase1" --webhook-secret "<shared-secret>" --webhook-retries 3 --webhook-backoff-seconds 1.0
python ".03_Harness Governance/orchestration/n8n/validate_workflow.py"
python ".03_Harness Governance/orchestration/n8n/import_workflow.py" --required-env "CHROMATIC_WEBHOOK_SECRET"

# Optional: API import into n8n
$env:N8N_BASE_URL="http://localhost:5678"
$env:N8N_API_KEY="<api-key>"
python ".03_Harness Governance/orchestration/n8n/import_workflow.py" --import-workflow
```

Webhook emission failures are logged as JSONL records at `.01_PDRs/.intake/drop_watcher-webhook-telemetry.jsonl`.

## LangGraph

- Dispatcher scaffold: `orchestration/langgraph/review_dispatch_graph.py`
- Runs without LangGraph in simulation mode and can be upgraded when `langgraph` is installed.
- Optional writeback mode updates queue status and emits mission/log artifacts.
- **Multi-session safety:** Uses PR branch locking to prevent concurrent mutations on the same PR.

Example:

```powershell
python ".03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py" --check-langgraph
python ".03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py" --queue-id "NW-REVIEW-INTAKE-001"
python ".03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py" --queue-id "NW-REVIEW-INTAKE-001" --writeback
```

Writeback now updates queue item status/metadata and persists mission packet artifacts under `.agents/review-intake/missions/`.

### Lock Coordination

When the dispatcher mutates a PR branch:

1. **Acquire lock** before patching:
   ```python
   python .01_PDRs/scripts/lock_pr_branch.py acquire \
     --repo kas1987/Chromatic_Governance --pr-number 1 \
     --holder "agent-dispatch-review-intake" \
     --queue-item-id "<queue_id>" --ttl-minutes 30
   ```
2. **Patch and validate** (commit locally, run tests)
3. **Push to branch**
4. **Release lock**:
   ```python
   python .01_PDRs/scripts/lock_pr_branch.py release \
     --repo kas1987/Chromatic_Governance --pr-number 1
   ```

See `.03_Harness Governance/03_PLAYBOOKS/MULTI_SESSION_SAFETY.md` for full collision safety procedures.
