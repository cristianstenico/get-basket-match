from lxml import html
from datetime import date, datetime, timedelta
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

class Match:
	def __init__(self, league, teamA, teamB, gameday, time, place):
		self.league = league
		self.teamA = teamA
		self.teamB = teamB
		self.gameday = gameday
		self.time = time
		self.place = place

	def save(self):
		dayafter = self.gameday + timedelta(1)
		calendar_id = [v for k, v in calendar_ids.items() if self.league in k][0]
		eventsResult = service.events().list(
			calendarId=calendar_id,
			timeMin= datetime.combine(self.gameday, datetime.min.time()).isoformat('T') + 'Z',
			timeMax=datetime.combine(dayafter, datetime.min.time()).isoformat('T') + 'Z').execute()
		if len(eventsResult.get('items', [])) == 0:
			print(self.teamA, self.teamB, self.gameday)

eventsResult = service.events().list(calendarId='primary', timeMin=datetime.utcnow().isoformat() + 'Z', maxResults=10, singleEvents=True, orderBy='startTime').execute()
events = eventsResult.get('items', [])

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

			# Se è presente la data vado avanti (in caso contrario, vuol dire che la partita è già stata giocata)
			if len(data_element) > 0:
				data = data_element[0].text.strip()

				# Controllo se una delle 2 squadre è il Gardolo
				if squadraA == 'BC GARDOLO' or squadraB == 'BC GARDOLO':
					
					data = re.fullmatch('(?P<giorno>\d\d)/(?P<mese>\d\d)/(?P<anno>\d\d\d\d) - (?P<ora>\d\d:\d\d)',data)
					giorno = date(int(data.group('anno')), int(data.group('mese')), int(data.group('giorno')))
					ora = data.group('ora')
					match = Match(squadre[campionato], squadraA, squadraB, giorno, ora, luogo)
					match.save()
				if squadraA == 'BC GARDOLO U20' or squadraB == 'BC GARDOLO U20':
					# print(f'{squadraA} - {squadraB}')
					# print(f'il {data} a {luogo}')
					print()
