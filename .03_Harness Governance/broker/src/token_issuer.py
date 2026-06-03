class GitHubAppTokenIssuer:
    """Token issuer placeholder.

    Production implementation should:
    1. Load the GitHub App private key from a secret store or secure file path.
    2. Generate a JWT for the GitHub App.
    3. Exchange it for an installation access token.
    4. Optionally narrow repositories and permissions at token creation time.
    5. Return the token only to trusted runtime code.

    Never log the token.
    """

    def __init__(self, app_id: str, private_key_path: str, api_version: str = "2026-03-10"):
        self.app_id = app_id
        self.private_key_path = private_key_path
        self.api_version = api_version

    def issue_token(self, installation_id: str, permissions: dict, repositories: list[str] | None = None) -> dict:
        raise NotImplementedError(
            "Wire this to PyJWT + requests, Octokit, or actions/create-github-app-token in GitHub Actions."
        )
