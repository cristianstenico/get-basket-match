from lxml import html
import requests
import re
squadre = {
	'U13/M': 'Under 13',
	'U14/M': 'Under 14',
	'U15/M': 'Under 15',
	'U16/M': 'Under 16',
	'U17/M': 'Under 17',
	'U18/M': 'Under 18',
	'PM': 'Promozione',
	'D': 'Serie D',
	'OPENM': 'Coppa Trentino'
}
# Scarico la homepage del sito Fip Trentino
home = requests.get('http://fip.it/risultati.asp?IDRegione=TN&com=RTN&IDProvincia=TN')

# Cerco i vari link delle categorie
for m in re.finditer('getCampionato\(\'RTN\', \'(?P<campionato>.+)\', \'(?P<fase>.+)\', \'(?P<codice>.+)\', (?P<andata>\d), (?P<turno>\d)\)', home.text):
	campionato = m.group('campionato')
	codice = m.group('codice')
	fase = m.group('fase')
	andata = m.group('andata')
	turno = m.group('turno')
	print('_' * 30)
	print()
	print(f' {squadre[campionato]} '.center(30, '-'))
	print()

	# Scarico la pagina con le date della categoria corrente
	page = requests.get(f'http://fip.it/AjaxGetDataCampionato.asp?com=RTN&camp={campionato}&fase={fase}&girone={codice}&ar={andata}&turno={turno}')

	# Cerco i link di tutte le giornate del campionato
	for m in re.finditer('getCampionato\(\'RTN\', \'(?P<campionato>.+)\', \'(?P<fase>.+)\', \'(?P<codice>.+)\', (?P<andata>\d), (?P<turno>\d)\)', page.text):
		campionato = m.group('campionato')
		codice = m.group('codice')
		fase = m.group('fase')
		andata = m.group('andata')
		turno = m.group('turno')

		# Scarico la pagina della singola giornata del campionato
		giornata = requests.get(f'http://fip.it/AjaxGetDataCampionato.asp?com=RTN&camp={campionato}&fase={fase}&girone={codice}&ar={andata}&turno={turno}')	
		tree = html.fromstring(giornata.content)

		# Scorro le partite e individuo squadre, data e luogo
		partite = tree.xpath('div[@class="risTr1"]')
		luoghi = tree.xpath('div[@class="risTr2"]')
		for i in range(len(partite)):
			partita = partite[i]
			luogo = luoghi[i].text.strip()
			squadraA = partita.xpath('.//div/a')[0].text.strip()
			squadraB = partita.xpath('.//div/a')[1].text.strip()
			data_element = partita.xpath('.//td[@class="risTr1P"]/font')
			data = (data_element[0] if len(data_element) > 0 else partita.xpath('.//td[@class="risTr1P"]')[0]).text.strip()

			# Controllo se una delle 2 squadre è il Gardolo
			if squadraA == 'BC GARDOLO' or squadraB == 'BC GARDOLO':
				print(f'{squadraA} - {squadraB}')
				print(f'il {data} a {luogo}')
				print()