from flask import Flask, escape, request

from . import smarty_client

app = Flask(__name__)


@app.route("/")
def hello():
    try:
        client = smarty_client.SmartyClient()
    except smarty_client.UnableToInitializeSmartyClient:
        return "SMARTY credentials (email and/or password) are missing."
    try:
        return client.get_usage()
    except smarty_client.UnableToGetUsage as e:
        return str(e)
