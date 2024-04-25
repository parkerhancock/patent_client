from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="patent_client_")
    base_dir: Path = Field(default=Path("~/.patent_client").expanduser())
    log_file: str = Field(default="patent_client.log")
    log_level: str = Field(default="INFO")
    epo_api_key: Optional[str] = Field(default=None)
    epo_api_secret: Optional[str] = Field(default=None)
    itc_username: Optional[str] = Field(default=None)
    itc_password: Optional[str] = Field(default=None)
    odp_api_key: Optional[str] = Field(default=None)
