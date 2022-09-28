import requests
from bs4 import BeautifulSoup
from rdkit import Chem
import json

def cpd2prop(inchikey):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/InChIKey/%s/property/MolecularFormula,XLogP,ExactMass,Charge/JSON" % inchikey
    resp = requests.get(url)
    if resp.status_code!=200:
        d = {}
    else:
        d = json.loads(resp.text)
        d = d['PropertyTable']['Properties'][0]

    curl = 'http://classyfire.wishartlab.com/entities/%s.json' % inchikey
    resp = requests.get(curl)
    if resp.status_code!=200:
        cd = {}
    else:
        cd = json.loads(resp.text)
        if 'kingdom' in cd.keys():
            d['kingdom'] = cd['kingdom']['name']
        if 'superclass' in cd.keys():
            d['superclass'] = cd['superclass']['name']
        if 'class' in cd.keys():
            d['class'] = cd['class']['name']
        if 'subclass' in cd.keys():
            d['subclass'] = cd['subclass']['name']

    return d