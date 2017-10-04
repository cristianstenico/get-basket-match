from lxml import html
import requests
page = requests.get('http://fip.it/risultati.asp?IDRegione=TN&com=RTN&IDProvincia=TN')
tree = html.fromstring(page.content)
print(tree.xpath('//script[getCampionato]/text()'))
