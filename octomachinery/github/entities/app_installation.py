"""GitHub App Installation wrapper."""

from __future__ import annotations

import logging
import typing

import attr

# pylint: disable=relative-beyond-top-level
from ..api.raw_client import RawGitHubAPI
# pylint: disable=relative-beyond-top-level
from ..api.tokens import GitHubOAuthToken
# pylint: disable=relative-beyond-top-level
from ..models import (
    GitHubAppInstallation as GitHubAppInstallationModel,
    GitHubInstallationAccessToken,
)


if typing.TYPE_CHECKING:
    from ..api.app_client import GitHubApp


logger = logging.getLogger(__name__)


@attr.dataclass
class GitHubAppInstallation:
    """GitHub App Installation API wrapper."""

    _metadata: GitHubAppInstallationModel
    """A GitHub Installation metadata from GitHub webhook."""
    _github_app: GitHubApp
    """A GitHub App the Installation is associated with."""
    _token: GitHubInstallationAccessToken = attr.ib(init=False, default=None)
    """A GitHub Installation token for GitHub API."""

    @property
    def app(self):
        """Bound GitHub App instance."""
        return self._github_app

    @property
    def token(self):
        """Return GitHub App Installation access token."""
        try:
            if self._token.expired:
                return None

            return GitHubOAuthToken(self._token.token)
        except TypeError:
            return None

    async def retrieve_access_token(self):
        """Retrieve installation access token from GitHub API."""
        self._token = GitHubInstallationAccessToken(**(
            await self.app.github_app_client.post(
                self._metadata.access_tokens_url,
                data=b'',
                preview_api_version='machine-man',
            )
        ))
        return self._token

    @property
    def api_client(self):  # noqa: D401
        """The GitHub App Installation client."""
        return RawGitHubAPI(
            token=self.token,
            # pylint: disable=protected-access
            session=self.app._http_session,
            # pylint: disable=protected-access
            user_agent=self.app._config.user_agent,
        )
