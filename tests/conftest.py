import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict

from sapwright import Sapwright


class SAPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    sap_username: str = ""
    sap_password: str = ""
    sap_connection_string: str = ""
    sap_connection_name: str = ""
    sap_client: int | None = None
    sap_language: str | None = None
    sap_terminate_other_sessions: bool = True


@pytest.fixture(scope="session")
def session():
    settings = SAPSettings()

    if not settings.sap_username:
        pytest.skip("SAP_USERNAME is not set in .env.test")

    if not settings.sap_password:
        pytest.skip("SAP_PASSWORD is not set in .env.test")

    if not settings.sap_connection_string and not settings.sap_connection_name:
        pytest.skip(
            "SAP_CONNECTION_STRING or SAP_CONNECTION_NAME is not set in .env.test"
        )

    sap = Sapwright(
        username=settings.sap_username,
        password=settings.sap_password,
        connection_string=settings.sap_connection_string,
        connection_name=settings.sap_connection_name,
        client=settings.sap_client,
        language=settings.sap_language,
        terminate_other_sessions=settings.sap_terminate_other_sessions,
    )
    session = sap.connect()
    yield session
    session.close_connection()
