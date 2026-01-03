# Uni Ulm Mensa Parser

This project contains a parser for the canteen / Mensa plans at
Ulm University that are provided on the
[Studierendenwerk Ulm website](https://studierendenwerk-ulm.de/essen-trinken/speiseplaene/).
You can see the data in action on the
[**UUlm Mensaplan website**](https://mensaplan.anter.dev/).

The parsed data is provided via a REST API as well:
[https://uulm.anter.dev/api/v1/canteens/all](https://uulm.anter.dev/api/v1/canteens/all)

The source code for the REST API is available at
[Tanikai/uniulm_mensa_api](https://github.com/Tanikai/uniulm_mensa_api).

## Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes.

### Prerequisites

This project is tested and deployed with Python 3.9+. The dependencies require
Python 3.8+.

### Integration into your own project

This project is still under active development, so I haven't released a Module
on PyPi yet. If you still want to use the current main branch in your project,
you can install the Module with the following command:

```sh
uv add git+https://github.com/Tanikai/uniulm_mensaparser@main
```

After installing, you can use the parser like this:
```Python
from uniulm_mensaparser import get_plan, Canteen, FsEtAdapter

# use get_plan() to get plans of all supported canteens
plan = get_plan()
print(plan)

# specify which canteen plans you want to be parsed in a set
my_canteens = {Canteen.UL_UNI_Sued, Canteen.UL_UNI_Nord}
# pass an adapter class for a different output format
plan = get_plan(my_canteens, adapter_class=FsEtAdapter)
print(plan)
```

### Installing for further development

If you want to extend the functionality of this library (e.g. implementing a new
Adapter or PDF parser), you can clone this repository and install the required
Python modules:

```sh
git clone https://github.com/Tanikai/uniulm_mensaparser.git
cd uniulm_mensaparser
uv sync
```

## Built With

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) to
  extract PDF links from the Studierendenwerk Ulm website
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) to scrape the tables of the canteen plan PDFs

## New MaxManager API endpoint

Since 2023, there is a new API endpoint for some canteens. This allows us to
parse the returned HTML, instead of the PDF file. The following curl command
sends a request to the new endpoint. Don't forget to replace the date with the
current date.

```bash
curl -X POST 'https://sw-ulm-spl51.maxmanager.xyz/inc/ajax-php_konnektor.inc.php?func=make_spl&locId=1&date=2023-07-20&lang=de&startThisWeek=2023-07-17&startNextWeek=2023-07-24'
```

## Authors

- **Kai Anter** - [GitHub](https://github.com/Tanikai) - [Mastodon](https://hachyderm.io/@Tanikai)

## License

This project is licensed under the GNU General Public License Version 3 - see
the [LICENSE](LICENSE) file for details
