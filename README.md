# Uni Ulm Mensa Parser

This project contains a parser for the canteen / mensa plans at
Ulm University that are provided on the
[Studierendenwerk Ulm website](https://studierendenwerk-ulm.de/essen-trinken/speiseplaene/).

The parsed data can be accessed here:
[uulm.anter.dev/api/v1/canteens/ul_uni_sued](https://uulm.anter.dev/api/v1/canteens/ul_uni_sued)

The source code for the REST API can be found at [github.com/Tanikai/uniulm_mensa_api](https://github.com/Tanikai/uniulm_mensa_api).

## Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes.

### Prerequisites

This project is tested and deployed with Python 3.9+. It might work with lower
versions, but without guarantee.

### Integration into your own project

This project is still under active development, so I haven't released a Module
on PyPi yet. If you still want to use the current main branch in your project,
you can install the Module with the following command:

```sh
pip install git+https://github.com/Tanikai/uniulm_mensaparser@main
```

After installing, you can use the parser like this:

```Python
from mensa_parser import parser, adapter
from mensa_parser.speiseplan_website_parser import Canteens

# specify which canteen plans you want to be parsed in a set
wanted_canteens = {Canteens.UL_UNI_Sued, Canteens.UL_UNI_West}

# Pass canteen set and reference to adapter class to parser
canteen_plan = parser.get_plans_for_canteens(wanted_canteens, adapter.SimpleAdapter)

print(canteen_plan)

```

### Installing for further development

If you want to extend the functionality of this library (e.g. implementing a new
Adapter or PDF parser), you can clone this repository and install the required
Python modules:

```sh
git clone https://github.com/Tanikai/uniulm_mensaparser.git
cd uniulm_mensaparser
pip install -r requirements.txt
```

## Built With

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for 
  extracting PDF links from the Studierendenwerk Ulm website
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for parsing the canteen plan
  PDF files

## Todo

- [ ] Adapter for the data schema by [Fachschaft Elektrotechik](https://mensaplan.fs-et.de/data/mensaplan.json)
- [ ] Add parser for Mensa Nord / Bistro 
- [ ] Better test coverage

## Authors

- **Kai Anter** - [GitHub](https://github.com/Tanikai) - [Twitter](https://twitter.com/tanikai29)

## License

This project is licensed under the GNU General Public License Version 3 - see
the [LICENSE.md](LICENSE.md) file for details
