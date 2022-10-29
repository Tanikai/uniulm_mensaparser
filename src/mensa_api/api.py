from flask import Flask, jsonify
from src.mensa_parser.speiseplan_website_parser import get_speiseplan, \
    simple_adapter
from cachetools import cached, TTLCache

appFlask = Flask(__name__)


@cached(cache=TTLCache(maxsize=4, ttl=3600))  # cache parsed plan for 1 hour
def get_cached_plan():
    print("parse plan...")
    plan = get_speiseplan()
    formatted = simple_adapter(plan)
    return formatted


@appFlask.route("/canteens/<mensa_id>/days/<date>/meals")
def return_mensaplan(mensa_id, date):
    formatted = get_cached_plan()
    try:
        day_plan = formatted[mensa_id][date]
        return jsonify(day_plan)
    except KeyError:
        return f"Could not find plan for {mensa_id} on date {date}", 404


if __name__ == "__main__":
    appFlask.run()
