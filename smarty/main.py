from flask import Flask, render_template, jsonify

from . import smarty_client

app = Flask(__name__)


@app.route("/")
def web_consumption():
    try:
        client = smarty_client.SmartyClient()
    except smarty_client.UnableToInitializeSmartyClient:
        return "SMARTY credentials (email and/or password) are missing."
    try:
        return render_template("index.html", usage=client.get_usage_as_text())
    except smarty_client.UnableToGetUsage as e:
        return str(e)


@app.route("/api/")
def api_consumption():
    try:
        client = smarty_client.SmartyClient()
    except smarty_client.UnableToInitializeSmartyClient:
        return "SMARTY credentials (email and/or password) are missing."
    try:
        return jsonify({
            "usage": client.get_usage_values()
        })
    except smarty_client.UnableToGetUsage as e:
        return str(e)
