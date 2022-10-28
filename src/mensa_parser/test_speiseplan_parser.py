from unittest import TestCase
import speiseplan_website_parser


class Test(TestCase):
    def test_get_speiseplan_website(self):
        source = speiseplan_website_parser.get_speiseplan_website()
        self.fail()

    def test_get_links(self):
        links = speiseplan_website_parser.get_links()
        pass
        self.fail()

    def test_parse_href(self):
        link = "https://studierendenwerk-ulm.de/wp-content/plugins/cortexmagick-wp/images/cache/speiseplaene/UL UNI Mensa Süd KW43 W2.pdf"
        given = speiseplan_website_parser.parse_href(link)
        expected = {
            "url": link,
            "mensa": speiseplan_website_parser.UniversityMensa.UL_UNI_Sued,
            "university_name": "Uni Ulm",
            "university_id": "UL",
            "mensa_name": "Mensa Süd",
            "week": "KW43",
        }
        self.assertEqual(expected["url"], given["url"])
        self.assertEqual(expected["mensa"], given["mensa"])
        #self.assertEqual(expected["university_id"], given["university_id"])
        #self.assertEqual(expected["mensa_name"], given["mensa_name"])
        self.assertEqual(expected["week"], given["week"])
    def test_get_meal_plans(self):
        plans = speiseplan_website_parser.get_speiseplan()
        self.fail()
