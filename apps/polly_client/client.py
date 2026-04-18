"""
Polly API Client for fetching polls from remote Polly server.
"""
import logging
from typing import Optional, List, Dict, Any
from django.conf import settings
import requests

logger = logging.getLogger(__name__)


class PollyAPIClient:
    """
    Client for interacting with remote Polly server API.
    Used to fetch polls for embedding in Byers Brands Portal.
    """

    def __init__(self):
        self.base_url = getattr(settings, 'POLLY_API_URL', 'http://localhost:8001')
        self.embedding_app = getattr(settings, 'POLLY_EMBEDDING_APP', 'byers-brands-llc')
        self.timeout = 10

    def get_polls(
        self,
        user_did: Optional[str] = None,
        theme: str = 'light',
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch polls for embedding.

        Args:
            user_did: User's DID for scope-aware filtering
            theme: 'light' or 'dark'
            limit: Maximum number of polls to return

        Returns:
            List of poll dictionaries
        """
        params = {
            'embedding_app': self.embedding_app,
            'theme': theme,
        }
        if user_did:
            params['user_did'] = user_did

        try:
            response = requests.get(
                f'{self.base_url}/api/embed/polls/',
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get('polls', [])[:limit]
        except requests.RequestException as e:
            logger.error(f"Failed to fetch polls: {e}")
            return []

    def get_poll(
        self,
        poll_id: int,
        user_did: Optional[str] = None,
        theme: str = 'light'
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single poll by ID.

        Args:
            poll_id: ID of the poll to fetch
            user_did: User's DID for scope-aware filtering
            theme: 'light' or 'dark'

        Returns:
            Poll dictionary or None if not found
        """
        params = {
            'embedding_app': self.embedding_app,
            'theme': theme,
        }
        if user_did:
            params['user_did'] = user_did

        try:
            response = requests.get(
                f'{self.base_url}/api/embed/polls/{poll_id}/',
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get('poll')
        except requests.RequestException as e:
            logger.error(f"Failed to fetch poll {poll_id}: {e}")
            return None

    def vote(
        self,
        poll_id: int,
        option_id: int,
        user_did: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Submit a vote to a poll.

        Args:
            poll_id: ID of the poll
            option_id: ID of the option being voted for
            user_did: User's DID
            signature: Cryptographic signature for the vote

        Returns:
            Response dictionary
        """
        data = {
            'poll_id': poll_id,
            'option_id': option_id,
            'voter_did': user_did,
            'signature': signature,
        }

        try:
            response = requests.post(
                f'{self.base_url}/api/polls/{poll_id}/vote/',
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to submit vote: {e}")
            return {'error': str(e)}

    def check_connection(self) -> bool:
        """
        Check if the Polly server is reachable.

        Returns:
            True if connected, False otherwise
        """
        try:
            response = requests.get(
                f'{self.base_url}/api/embed/polls/',
                params={'embedding_app': self.embedding_app},
                timeout=5
            )
            return response.status_code in (200, 400, 401)
        except requests.RequestException:
            return False


def get_polly_client() -> PollyAPIClient:
    """Get a Polly API client instance."""
    return PollyAPIClient()