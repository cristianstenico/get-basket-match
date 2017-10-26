from datetime import date, time, datetime, timedelta
from pytz import timezone
import re

romeTimeZone = timezone('Europe/Rome')

class Game:
	def __init__(self, league, gameData, place):
		self.league = league
		self.teamA = gameData.xpath('.//div/a')[0].text.strip()
		self.teamB = gameData.xpath('.//div/a')[1].text.strip()
		self.summary = f'{self.league}: {self.teamA} vs {self.teamB}'
		self.place = place
		self.isGardolo = self.teamA == 'BC GARDOLO' or self.teamB == 'BC GARDOLO'
		self.isUnder20 = self.teamA == 'BC GARDOLO U20' or self.teamB == 'BC GARDOLO U20'
		if self.isGardolo or self.isUnder20:
			dateData = gameData.xpath('.//td[@class="risTr1P"]/font')
			# Se è presente la data, la partita non è ancora stata giocata, posso quindi salvarla su calendar 
			if len(dateData) > 0:
				self.futureGame = True
				data = re.fullmatch('(?P<day>\d\d)/(?P<month>\d\d)/(?P<year>\d\d\d\d) - (?P<time>\d\d:\d\d)', dateData[0].text.strip())
				self.gameday = date(int(data.group('year')), int(data.group('month')), int(data.group('day')))
				self.time = time(*map(int, data.group('time').split(':')))
				if self.isUnder20:
					self.league = 'Under 20'
					self.summary = f'{self.league}: {self.teamA} vs {self.teamB}'
			else:
				self.futureGame = False
				self.result = gameData.xpath('.//td[@class="risTr1P"]')[0].text.strip()


	def check(self, service, id):
		timeMin = datetime.combine(self.gameday, self.time) + timedelta(minutes=89)
		timeMax = datetime.combine(self.gameday, self.time) + timedelta(minutes=1)

		# Controllo lower-bound
		eventsResult = service.events().list(
			calendarId = id,
			q = f'"{self.summary}"',
			timeMax = romeTimeZone.localize(timeMax).isoformat('T'),
			maxResults = 1).execute()

		if len(eventsResult.get('items', [])) == 0:
			return True

		# Controllo upper-bound
		eventsResult = service.events().list(
			calendarId = id,
			q = f'"{self.summary}"',
			timeMin = romeTimeZone.localize(timeMin).isoformat('T'),
			maxResults = 1).execute()

		if len(eventsResult.get('items', [])) == 0:
			return True
		return False

	def save(self, service, cal_id):
		if self.futureGame:
			if self.check(service, cal_id):
				print(f'        Inserisco la partita nel calendario')
				start = datetime.combine(self.gameday, self.time)
				end = start + timedelta(minutes=90)	
				match = {
					'summary': self.summary,
					'location': self.place,
					'description': self.league,
					'start': {
					  	'dateTime': start.isoformat('T'),
					  	'timeZone': 'Europe/Rome'
					},
					'end': {
					  	'dateTime': end.isoformat('T'),
					  	'timeZone': 'Europe/Rome'
					},
					'reminders': {
						'useDefault': False,
						'overrides': [
							{'method': 'popup', 'minutes': 60}
						],
					},
				}
				res = service.events().insert(calendarId = cal_id, body = match).execute()
				print(self.teamA, self.teamB, self.gameday)
		else:
			print(f'{self.teamA} - {self.teamB}: {self.result}')