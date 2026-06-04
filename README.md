# Chromatic Governance

Chromatic Governance is a policy and orchestration repository for AI-assisted software delivery.

It contains:
- PDR artifacts and governance records
- plugin and skill governance toolchains
- workflow automation for intake, review, and promotion
- harness scripts for safe, auditable dispatch and execution

## Repository Layout

- .01_PDRs: product, design, and governance records
- .02_Plugins: plugin families and validation tooling
- .03_Harness Governance: orchestration scripts, tests, and runtime controls
- .github: CI, governance workflows, templates, and automation rules

## Local Validation

From repository root:

```powershell
python -m pytest ".03_Harness Governance/scripts/tests/test_dispatch.py" -q
```

## Security and Reporting

- Review [SECURITY.md](SECURITY.md) for vulnerability reporting.
- Do not commit secrets, tokens, or private keys.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening pull requests.

## License

This repository is licensed under the MIT License. See [LICENSE](LICENSE).
