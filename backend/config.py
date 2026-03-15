from functools import lru_cache
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    inventory_dataset_url: str = (
        "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
    )
    inventory_dataset_path: str = "data/online_retail_sample.csv"
    api_title: str = "AI Inventory Predictor API"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value

        normalized = value.replace("postgres://", "postgresql://", 1)
        scheme, separator, remainder = normalized.partition("://")
        if separator:
            netloc, path_separator, path = remainder.partition("/")
            if netloc.count("@") > 1:
                userinfo, hostinfo = netloc.rsplit("@", 1)
                username, credential_separator, password = userinfo.partition(":")
                encoded_userinfo = quote(username, safe="")
                if credential_separator:
                    encoded_userinfo = f"{encoded_userinfo}:{quote(password, safe='')}"
                normalized = f"{scheme}://{encoded_userinfo}@{hostinfo}"
                if path_separator:
                    normalized = f"{normalized}/{path}"

        parsed = urlsplit(normalized)
        if not parsed.query:
            return normalized

        filtered_query = [
            (key, item)
            for key, item in parse_qsl(parsed.query, keep_blank_values=True)
            if key.lower() != "pgbouncer"
        ]

        return urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, urlencode(filtered_query), parsed.fragment)
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
