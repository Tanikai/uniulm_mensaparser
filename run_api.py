from mensa_api import flask_api

application = flask_api.create_app()

if __name__ == "__main__":
    app = flask_api.create_app()
    app.run()

