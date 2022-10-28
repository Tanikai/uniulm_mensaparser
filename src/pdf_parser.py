import os
import logging
import json
import datetime
import urllib
from pdfminer.high_level import extract_text_to_fp, extract_text
import speiseplan_website_parser
from pdfminer.layout import LAParams
from io import StringIO

roles = ('student', 'employee', 'other')
weekdays = ('Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday')

legend = {
    'S': "Schwein",
    'R': "Rind",
    'G': "Geflügel",
    '1': "Farbstoff",
    '2': "Konservierungsstoff",
    '3': "Antioxidationsmittel",
    '4': "Geschmacksverstärker",
    '5': "geschwefelt",
    '6': "geschwärzt",
    '7': "gewachst",
    '8': "Phosphat",
    '9': "Süßungsmitteln",
    '10': "Phenylalani",
    '13': "Krebstieren",
    '14': "Ei",
    '22': "Erdnuss",
    '23': "Soja",
    '24': "Milch/Milchprodukte",
    '25': "Schalenfrucht (alle Nussarten)",
    '26': "Sellerie",
    '27': "Senf",
    '28': "Sesamsamen",
    '29': "Schwefeldioxid",
    '30': "Sulfit",
    '31': "Lupine",
    '32': "Weichtiere",
    '34': "Gluten",
    '35': "Fisch"
}


def parse_all():
    urls = speiseplan_website_parser.get_links()
    parse_pdf(urls[0])


def parse_pdf(pdf_url: str):
    with open(pdf_url) as pdf_file:
        parse_pdf_file(pdf_file)


def parse_pdf_file(pdf_file):
    output_string = StringIO()
    extract_text_to_fp(pdf_file, output_string, laparams=LAParams(),
                       output_type="html", codec=None)
    print(output_string.read())
    pass
