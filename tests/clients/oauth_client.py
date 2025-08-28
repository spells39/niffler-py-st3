import base64
import os

import pkce
from dotenv import load_dotenv

from tests.models.config import Envs
from tests.models.oauth import OAuthRequest
from tests.utils.sessions import AuthSession

load_dotenv()
front_url = os.getenv("FRONT_URL")

class OAuthClient:
    """Авториизует по Oauth2.0"""

    session: AuthSession
    base_url: str

    def __init__(self, env: Envs):
        """Генерируем code_verifier и code_challenge. И генерируем basic auth token из секрета сервиса авторизации."""
        self.session = AuthSession(base_url=env.auth_url)
        self.code_verifier, self.code_challenge = pkce.generate_pkce_pair()

        self._basic_token = base64.b64encode(env.auth_secret.encode('utf-8')).decode('utf-8')
        self.authorization_basic = {"Authorization": f"Basic {self._basic_token}"}
        self.token = None

    def get_token(self, username, password, envs: Envs):
        """Возвраащает token oauth для авторизации пользователя с username и password
        1. Получаем jsessionid и xsrf-token куку в сесссию.
        2. Получаем code из redirec по xsrf-token'у.
        3. Получаем access_token.
        """
        try:
            OAuthClient(envs).register(username, password, envs)
        except Exception as e:
            pass
        self.session.get(
            url="/oauth2/authorize",
            params=OAuthRequest(
                redirect_uri=f"{envs.front_url}/authorized",
                code=self.session.code,
                code_challenge=self.code_challenge
            ).model_dump(),
            allow_redirects=True
        )

        self.session.post(
            url="/login",
            data={
                "username": username,
                "password": password,
                "_csrf": self.session.cookies.get("XSRF-TOKEN")
            },
            allow_redirects=True
        )

        token_response = self.session.post(
            url="/oauth2/token",
            data={
                "code": self.session.code,
                "redirect_uri": f"{envs.front_url}/authorized",
                "code_verifier": self.code_verifier,
                "grant_type": "authorization_code",
                "client_id": "client"
            },
        )
        self.token = token_response.json().get("access_token", None)
        return self.token

    def register(self, username, password, envs: Envs, expect_error: bool = False):
        if expect_error:
            self.session.get(
                url=f"{envs.auth_url}/register",
                params={
                    "redirect_uri": "http://auth.niffler.dc:9000/register",
                },
                allow_redirects=True,
                skip_status_check=True
            )

            result = self.session.post(
                url=f"{envs.auth_url}/register",
                data={
                    "username": username,
                    "password": password,
                    "passwordSubmit": password,
                    "_csrf": self.session.cookies.get("XSRF-TOKEN")
                },
                allow_redirects=True,
                skip_status_check=True
            )
        else:
            self.session.get(
                url=f"{envs.auth_url}/register",
                params={
                    "redirect_uri": "http://auth.niffler.dc:9000/register",
                },
                allow_redirects=True
            )

            result = self.session.post(
                url=f"{envs.auth_url}/register",
                data={
                    "username": username,
                    "password": password,
                    "passwordSubmit": password,
                    "_csrf": self.session.cookies.get("XSRF-TOKEN")
                },
                allow_redirects=True
            )
        return result