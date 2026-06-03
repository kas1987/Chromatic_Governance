# Source Notes

This kit is aligned with current GitHub App and GitHub Actions access patterns:

- GitHub Apps can authenticate as an app installation using installation access tokens.
- Installation access tokens can be narrowed by repository and permissions and expire after a limited period.
- GitHub Actions can use `actions/create-github-app-token` for app-token creation inside workflows.
- `GITHUB_TOKEN` is useful for same-repository workflow automation, but a GitHub App is preferred for broader app-style integrations and selected-repo governance.

Always re-check GitHub Docs before production rollout because API versions, token formats, and Actions versions can change.
