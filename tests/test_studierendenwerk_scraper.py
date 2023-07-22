from unittest import TestCase
import uniulm_mensaparser.studierendenwerk_scraper
from uniulm_mensaparser.models import Canteen, Plan


class TestSpeiseplanWebsiteParser(TestCase):
    def test_parse_href(self):
        link = (
            "https://studierendenwerk-ulm.de/wp-content/plugins"
            "/cortexmagick-wp/images/cache/speiseplaene/UL UNI Mensa Süd "
            "KW43 W2.pdf "
        )
        given = uniulm_mensaparser.studierendenwerk_scraper._parse_legacy_pdf_name(link)
        expected = Plan(url=link, canteen=Canteen.UL_UNI_Sued, week="KW43")
        self.assertEqual(expected, given)

    def test_html_scrape(self):
        with open("html/20230330.htm") as f:
            links = uniulm_mensaparser.studierendenwerk_scraper._scrape_legacy_pdf_urls(
                f.read()
            )
            self.assertFalse(links == [], "No links found")
            self.assertEqual(
                2, len(list(filter(lambda x: x.canteen == Canteen.UL_UNI_Nord, links)))
            )
            self.assertEqual(
                2, len(list(filter(lambda x: x.canteen == Canteen.UL_UNI_Sued, links)))
            )
