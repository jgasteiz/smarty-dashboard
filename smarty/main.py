from flask import Flask, render_template, jsonify, send_from_directory

from . import smarty_client

app = Flask(__name__,  static_url_path='')


@app.route("/")
def web_consumption():
    return render_template("index.html")


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


@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)
