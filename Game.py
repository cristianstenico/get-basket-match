from datetime import date, time, datetime, timedelta
import re
class Game:
	def __init__(self, league, gameData, place):
		self.league = league
		self.teamA = gameData.xpath('.//div/a')[0].text.strip()
		self.teamB = gameData.xpath('.//div/a')[1].text.strip()
		self.place = place
		self.isGardolo = self.teamA == 'BC GARDOLO' or self.teamB == 'BC GARDOLO'
		self.isUnder20 = self.teamA == 'BC GARDOLO U20' or self.teamB == 'BC GARDOLO U20'
		if self.isGardolo or self.isUnder20:
			dateData = gameData.xpath('.//td[@class="risTr1P"]/font')
			if len(dateData) > 0:
				data = re.fullmatch('(?P<day>\d\d)/(?P<month>\d\d)/(?P<year>\d\d\d\d) - (?P<time>\d\d:\d\d)', dateData[0].text.strip())
				self.gameday = date(int(data.group('year')), int(data.group('month')), int(data.group('day')))
				self.time = time(*map(int,data.group('time').split(':')))
				if self.isUnder20:
					print(self.league)

	def check(self, service, id):
		dayafter = self.gameday + timedelta(1)
		eventsResult = service.events().list(
			calendarId=id,
			timeMin= datetime.combine(self.gameday, datetime.min.time()).isoformat('T') + 'Z',
			timeMax=datetime.combine(dayafter, datetime.min.time()).isoformat('T') + 'Z').execute()
		return len(eventsResult.get('items', [])) == 0

	def save(self, service, cal_id):
		if self.check(service, cal_id):
			print(f'        Inserisco la partita nel calendario')
			start = datetime.combine(self.gameday, self.time)
			end = start + timedelta(minutes=90)
			match = {
				'summary': f'{self.league}: {self.teamA} vs {self.teamB}',
				'location': self.place,
				'description': self.league,
				'start': {
				  	'dateTime': start.isoformat(),
				  	'timeZone': 'Europe/Rome'
				},
				'end': {
				  	'dateTime': end.isoformat(),
				  	'timeZone': 'Europe/Rome'
				},
				'reminders': {
					'useDefault': False,
					'overrides': [
						{'method': 'popup', 'minutes': 60}
					],
				},
			}
			res = service.events().insert(calendarId=cal_id, body=match).execute()
			print(self.teamA, self.teamB, self.gameday)