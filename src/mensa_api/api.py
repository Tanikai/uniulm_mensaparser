from flask import Flask, jsonify
import src.mensa_parser.speiseplan_website_parser

appFlask = Flask(__name__)

@appFlask.route("/data/mensaplan.json")
def return_mensaplan():
    pass


if __name__ == "__main__":
    appFlask.run()
