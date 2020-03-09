import json
from decimal import Decimal as D

import requests

from . import db_client, settings


class UnableToInitializeSmartyClient(Exception):
    pass


class UnableToGetUsage(Exception):
    pass


class SmartyClient:
    AUTH_URL = "https://smarty.co.uk/api/v1/users/token"
    USAGE_URL = "https://smarty.co.uk/api/v1/usage"

    def __init__(self):
        if not settings.SMARTY_EMAIL or not settings.SMARTY_PASSWORD:
            raise UnableToInitializeSmartyClient()
        self.email = settings.SMARTY_EMAIL
        self.password = settings.SMARTY_PASSWORD

    def get_usage(self, retry=True):
        """
        Get the remaining usage.
        """
        headers = {"Authorization": self._get_authorization_header()}
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
        return f"{round(remaining_gb, 2)}GB left of {limit_gb}GB"

    def _get_authorization_header(self):
        """
        Get the authorization header value.
        """
        return f"Bearer {self._get_token()}"

    def _get_token(self):
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

    def _save_token(self, token):
        db = db_client.DBClient.get_db()
        db["token"] = token
        db_client.DBClient.update_db(db)

    def _clear_token(self):
        db = db_client.DBClient.get_db()
        del db["token"]
        db_client.DBClient.update_db(db)
