# Uni Ulm Mensa Parser

This project contains a parser for the canteen / mensa plans at
Ulm University that are provided on the
[Studierendenwerk Ulm website](https://studierendenwerk-ulm.de/essen-trinken/speiseplaene/).

The parsed data can be accessed here:
[uulm.anter.dev/api/v1/canteens/ul_uni_sued](https://uulm.anter.dev/api/v1/canteens/ul_uni_sued)
The source code for the REST API can be found at [Tanikai/uniulm_mensa_api](https://github.com/Tanikai/uniulm_mensa_api).

## Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes.

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

## Built With

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for 
  extracting PDF links from the Studierendenwerk Ulm website
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for parsing the canteen plan
  pdf files

## Todo

- [ ] Adapter for the data schema by [Fachschaft Elektrotechik](https://mensaplan.fs-et.de/data/mensaplan.json)
- [ ] Support for other canteens at Ulm University
- [ ] Better test coverage

## Authors

- **Kai Anter** - [GitHub](https://github.com/Tanikai) - [Twitter](https://twitter.com/tanikai29)

## License

This project is licensed under the GNU General Public License Version 3 - see
the [LICENSE.md](LICENSE.md) file for details
