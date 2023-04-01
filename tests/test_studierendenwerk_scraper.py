from unittest import TestCase
from uniulm_mensaparser.studierendenwerk_scraper import parse_pdf_name, scrape_pdf_links
from uniulm_mensaparser.models import Canteens, Plan


class TestSpeiseplanWebsiteParser(TestCase):

    def test_parse_href(self):
        link = "https://studierendenwerk-ulm.de/wp-content/plugins" \
               "/cortexmagick-wp/images/cache/speiseplaene/UL UNI Mensa Süd " \
               "KW43 W2.pdf "
        given = parse_pdf_name(link)
        expected = Plan(
            url=link,
            canteen=Canteens.UL_UNI_Sued,
            week="KW43"
        )
        self.assertEqual(expected, given)

    def test_html_scrape(self):
        with open("html/20230330.htm") as f:
            links = scrape_pdf_links(f.read())
            self.assertFalse(links == [], "No links found")
            self.assertEqual(2, len(list(filter(lambda x: x.canteen == Canteens.UL_UNI_Nord, links))))
            self.assertEqual(2, len(list(filter(lambda x: x.canteen == Canteens.UL_UNI_Sued, links))))
