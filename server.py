#!/usr/bin/env python3
import os
import sys
import datetime
import markovify
from flask import Flask, request, render_template, redirect, send_from_directory, abort
import exportModel
from twitterTools import TwitterTools

app = Flask(__name__)

twitterKeys = { "CK": os.environ.get("TWITTER_API_CONKEY"), "CS": os.environ.get("TWITTER_API_CONSEC") }

def generateFromReq(filename, startWith, length):
    try:
        with open(filename) as f:
            textModel = markovify.Text.from_json(f.read())
        if startWith:
            sentence = "".join(textModel.make_sentence_with_start(startWith, tries = 100).split())
        elif length:
            sentence = "".join(textModel.make_short_sentence(length, tries = 100).split())
        else:
            sentence = "".join(textModel.make_sentence(tries = 100).split())
    except Exception as e:
        print(e)
        sentence = "生成失敗"
    print(sentence)
    return sentence


# static resources
@app.route("/resources/<path>")
def resources(path):
    return send_from_directory("resources", path)


# Twitter related pages
@app.route("/twitter/authLink")
def twitterAuthLink():
    global twitterKeys
    if "callback" not in request.args:
        abort(400)
    twt = TwitterTools(twitterKeys["CK"], twitterKeys["CS"], None, None, request.args["callback"])
    return redirect(twt.getAuthenticateURL())

@app.route("/twitter/authAndGen")
def twitterAuthAndGen():
    global twitterKeys
    htmldisp = { "error": None, "success": None }
    try:
        twt = TwitterTools(twitterKeys["CK"], twitterKeys["CS"], None, None)
        twt.oauth.parse_authorization_response(request.url)
        token = twt.oauth.fetch_access_token("https://api.twitter.com/oauth/access_token")
        twt = TwitterTools(twitterKeys["CK"], twitterKeys["CS"], token["oauth_token"], token["oauth_token_secret"])
        params = { "screen_name": token["screen_name"], "trim_user": 1 }
        filepath = os.path.join("./chainfiles", token["screen_name"] + ".json")
        if (os.path.getmtime(filepath) - datetime.now().timestamp() < 60 * 60 * 24):
            htmldisp["error"] = "You can generate Markov chain only once per 24 hours."
            return render_template("index.html", htmldisp = htmldisp)
        exportModel.generateAndExport(exportModel.loadTwitterAPI(twt, params), filepath)
        htmldisp["success"] = token["screen_name"] + "'s Markov chain model was successfully GENERATED!"
    except Exception as e:
        print(e)
        htmldisp["error"] = "Failed to generate your Markov chain. Please retry a few minutes later."
    return render_template("index.html", htmldisp = htmldisp)


# main page
@app.route("/", methods = ["GET", "POST"])
@app.route("/<filename>", methods = ["GET", "POST"])
def index(filename = None):
    htmldisp = {
        "sentence": None,
        "error": None,
        "success": None,
        "startWith": None,
        "length": None
    }
    if request.method == "POST":
        htmldisp["startWith"] = request.form["startWith"] if "startWith" in request.form and len(request.form["startWith"]) > 0 else None
        htmldisp["length"] = int(request.form["length"]) if "length" in request.form and request.form["length"].isdecimal() else None
        if "filename" in request.form and request.form["filename"] != filename:
            filename = os.path.basename(request.form["filename"])
            if os.path.isfile("./chainfiles/" + filename + ".json"):
                return redirect("/" + filename, code = 307)
            else:
                htmldisp["error"] = "Specified file not found!"
        elif filename is not None:
            filename = os.path.basename(filename)
            if os.path.isfile("./chainfiles/" + filename + ".json"):
                htmldisp["sentence"] = generateFromReq("./chainfiles/" + filename + ".json", htmldisp["startWith"], htmldisp["length"])
            else:
                htmldisp["error"] = "Specified file not found!"

    return render_template("cordx56.html" if filename == "cordx56" else "index.html", filename = filename, htmldisp = htmldisp)


if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.run(host = "0.0.0.0", port = port)
