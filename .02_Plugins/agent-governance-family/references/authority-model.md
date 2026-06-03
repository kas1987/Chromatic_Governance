# Authority Model

## Authority levels

| Level | Meaning |
|---|---|
| observe | Read and summarize only |
| recommend | Suggest a plan but do not modify files |
| draft | Create proposed content/artifacts for review |
| modify | Edit files inside approved scope |
| approve | Accept or reject another actor's work |
| execute | Run commands or perform external actions |
| forbidden | Must not perform the action |

## Action categories

- File read
- File write
- Command execution
- Network calls
- Secrets access
- Dependency changes
- Git branch/commit/merge
- Deployment/release
- Data deletion
- External communication

## Default stance

Agents start at observe/recommend. Upgrade authority only for a bounded task and only when the risk is understood.
