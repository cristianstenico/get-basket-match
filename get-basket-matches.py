from lxml import html
from datetime import date, datetime, timedelta, time
from Game import Game
import requests
import credentials
import re
squadre = {
	'U13/M': 'Under 13',
	'U14/M': 'Under 14',
	'U15/M': 'Under 15',
	'U16/M': 'Under 16',
	'U17/M': 'Under 17',
	'U18/M': 'Under 18',
	'U20': 'Under 20',
	'PM': 'Promozione',
	'D': 'Serie D',
	'OPENM': 'Coppa Trentino'
}

calendar_ids = {}

# Inizializzo il servizio di Google Calendar
service = credentials.get_service()

# Salvo l'id dei vari calendari
calendars = service.calendarList().list().execute()
for item in calendars.get('items', []):
	calendar_ids[item['summary']] = item['id']

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
		games = tree.xpath('div[@class="risTr1"]')
		places = tree.xpath('div[@class="risTr2"]')
		for i in range(len(games)):
			# Inizializzo l'oggetto Game 
			game = Game(league=squadre[campionato], gameData=games[i], place=places[i].text.strip())
			if game.isGardolo:
				game.save(service, cal_id=[v for k, v in calendar_ids.items() if squadre[campionato] in k][0])
