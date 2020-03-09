from datetime import datetime, timedelta
from decimal import Decimal as D
from typing import Optional

import requests

from . import db_client, settings


class UnableToInitializeSmartyClient(Exception):
    pass


class UnableToGetUsage(Exception):
    pass


class SmartyClient:
    AUTH_URL = "https://smarty.co.uk/api/v1/users/token"
    USAGE_URL = "https://smarty.co.uk/api/v1/usage"
    DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self):
        if not settings.SMARTY_EMAIL or not settings.SMARTY_PASSWORD:
            raise UnableToInitializeSmartyClient()
        self.email = settings.SMARTY_EMAIL
        self.password = settings.SMARTY_PASSWORD

    def get_usage(self, retry: bool = True) -> str:
        """
        Get the remaining usage.
        """
        # If we have a recent enough cached usage, return that.
        saved_usage = self._get_saved_usage()
        if saved_usage:
            return saved_usage

        # Otherwise, get the usage from the API.
        headers = {"Authorization": f"Bearer {self._get_token()}"}
        response = requests.get(self.USAGE_URL, headers=headers)
        if retry and response.status_code == 401:
            self._clear_token()
            return self.get_usage(retry=False)
        elif response.status_code != 200:
            raise UnableToGetUsage(f"{response.status_code} - Unable to get usage")

        response_json = response.json()

        plan = response_json["data"]["attributes"]["plan"]["bundles"][2]
        limit = D(plan["limit"]["value"])
        used = D(plan["used"]["value"])
        remaining_gb = (limit - used) / D("1024") / D("1024")
        limit_gb = limit / D("1024") / D("1024")
        usage = f"{round(remaining_gb, 2)}GB left of {limit_gb}GB"

        # Cache the usage.
        self._save_usage(usage)

        return usage

    def _get_token(self) -> str:
        db = db_client.DBClient.get_db()
        if "token" in db:
            return db["token"]
        payload = {"auth": {"email": self.email, "password": self.password}}
        response = requests.post(self.AUTH_URL, json=payload)
        if response.status_code != 201:
            raise UnableToGetUsage(f"{response.content} - Unable to authenticate")
        response_json = response.json()
        token = response_json["data"]["attributes"]["jwt"]
        self._save_token(token)
        return token

    def _save_token(self, token: str):
        db = db_client.DBClient.get_db()
        db["token"] = token
        db_client.DBClient.update_db(db)

    def _clear_token(self):
        db = db_client.DBClient.get_db()
        del db["token"]
        db_client.DBClient.update_db(db)

    def _save_usage(self, usage: str):
        db = db_client.DBClient.get_db()
        db["usage"] = {"value": usage, "updated_at": self._get_timestamp()}
        db_client.DBClient.update_db(db)

    def _get_saved_usage(self) -> Optional[str]:
        db = db_client.DBClient.get_db()
        if "usage" in db:
            try:
                updated_at = datetime.strptime(
                    db["usage"]["updated_at"], self.DATE_TIME_FORMAT
                )
            except (KeyError, ValueError):
                return None
            if updated_at > datetime.now() - timedelta(minutes=5):
                return db["usage"]["value"]
        return None

    def _get_timestamp(self) -> str:
        return datetime.now().strftime(self.DATE_TIME_FORMAT)
