# Orchestration Scaffolds

This folder contains implementation-ready orchestration assets referenced by the PDR automation docs.

## n8n

- Workflow JSON: `orchestration/n8n/pdr-zip-intake-phase1.workflow.json`
- Import this file into n8n and set environment variable `CHROMATIC_WEBHOOK_SECRET`.
- Validator: `orchestration/n8n/validate_workflow.py`
- Trigger endpoint path: `/webhook/pdr-zip-intake-phase1`

Expected local bridge command:

```powershell
python .01_PDRs/pdr_zip_ingest.py watch --webhook-url "http://localhost:5678/webhook/pdr-zip-intake-phase1" --webhook-secret "<shared-secret>"
python ".03_Harness Governance/orchestration/n8n/validate_workflow.py"
```

## LangGraph

- Dispatcher scaffold: `orchestration/langgraph/review_dispatch_graph.py`
- Runs without LangGraph in simulation mode and can be upgraded when `langgraph` is installed.
- Optional writeback mode updates queue status and emits mission/log artifacts.

Example:

```powershell
python ".03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py" --check-langgraph
python ".03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py" --queue-id "NW-REVIEW-INTAKE-001"
python ".03_Harness Governance/orchestration/langgraph/review_dispatch_graph.py" --queue-id "NW-REVIEW-INTAKE-001" --writeback
```
