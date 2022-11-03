# Uni Ulm Mensa Parser

This project contains a parser for the canteen / mensa plans at
Ulm University that are provided on the
[Studierendenwerk Ulm website](https://studierendenwerk-ulm.de/essen-trinken/speiseplaene/).

The parsed data can be accessed here:
[uulm.anter.dev/api/v1/canteens/ul_uni_sued](https://uulm.anter.dev/api/v1/canteens/ul_uni_sued)

## Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes. See deployment
for notes on deploying the project on a live system.

### Prerequisites

This project is tested and deployed with Python 3.9+. It might work with lower
versions, but without guarantee.

### Installing

Firstly, clone this repository and install the required Python modules:

```sh
git clone https://github.com/Tanikai/uniulm_mensaparser.git
cd uniulm_mensaparser
pip install -r requirements.txt
```

After that, you can run the REST API with:

```sh
python run_api.py
```

## Deployment

When you want to deploy the application, you will need a WSGI server. For
example, you can use the [waitress](https://github.com/Pylons/waitress) module:

```sh
python -m waitress --port 8080 run_api:application
```

## API Documentation

| Path                                                       | Description                                                                        |
|------------------------------------------------------------|------------------------------------------------------------------------------------|
| BASE_URL/api/v1/canteens/ul_uni_sued/                      | Get the next plan for the Mensa Süd (days where the canteen is closed are skipped) |
| BASE_URL/api/v1/canteens/ul_uni_sued/days/YYYY-MM-DD/meals | Get the mensa plan for a specific day                                              |

## Built With

  - [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for 
    extracting PDF links from the Studierendenwerk Ulm website
  - [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for parsing the canteen plan
    pdf files
  - [flask](https://flask.palletsprojects.com/) for the REST API

## Todo

- [ ] Adapter for the data schema by [Fachschaft Elektrotechik](https://mensaplan.fs-et.de/data/mensaplan.json)
- [ ] Support for other canteens at Ulm University
- [ ] Better test coverage

## Authors

 - **Kai Anter** - [GitHub](https://github.com/Tanikai) - [Twitter](https://twitter.com/tanikai29)

## License

This project is licensed under the GNU General Public License Version 3 - see
the [LICENSE.md](LICENSE.md) file for details
