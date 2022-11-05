from unittest import TestCase
from mensa_parser.speiseplan_website_parser import parse_pdf_name, \
    get_speiseplan, Canteens

class TestSpeiseplanWebsiteParser(TestCase):

    def test_parse_href(self):
        link = "https://studierendenwerk-ulm.de/wp-content/plugins" \
               "/cortexmagick-wp/images/cache/speiseplaene/UL UNI Mensa Süd " \
               "KW43 W2.pdf "
        given = parse_pdf_name(link)
        expected = {
            "url": link,
            "mensa": Canteens.UL_UNI_Sued,
            "university_name": "Uni Ulm",
            "university_id": "UL",
            "mensa_name": "Mensa Süd",
            "week": "KW43",
        }
        self.assertEqual(expected["url"], given["url"])
        self.assertEqual(expected["mensa"], given["mensa"])
        # self.assertEqual(expected["university_id"], given["university_id"])
        # self.assertEqual(expected["mensa_name"], given["mensa_name"])
        self.assertEqual(expected["week"], given["week"])

    def test_get_speiseplan(self):
        links = get_speiseplan({Canteens.UL_UNI_Sued})
        for l in links:
            self.assertTrue("UL UNI Mensa Süd" in l["url"])
        links = get_speiseplan({Canteens.UL_UNI_West})
        for l in links:
            self.assertTrue("UL UNI West" in l["url"])
        links = get_speiseplan({Canteens.UL_UNI_Nord})
        for l in links:
            self.assertTrue("UL UNI Nord" in l["url"])
