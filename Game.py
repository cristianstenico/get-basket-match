from datetime import date, time, datetime, timedelta
from pytz import timezone
import re

romeTimeZone = timezone('Europe/Rome')


class Game:
    def __init__(self, league, gameData, place):
        self.league = [league]
        self.teamA = gameData.xpath('.//div/a')[0].text.strip()
        self.teamB = gameData.xpath('.//div/a')[1].text.strip()
        self.place = place
        self.isGardolo = self.teamA == 'BC GARDOLO' or self.teamB == 'BC GARDOLO' or self.teamA == 'MB GARDOLO' or self.teamB == 'MB GARDOLO'
        self.isUnder20 = self.teamA == 'BC GARDOLO U20' or self.teamB == 'BC GARDOLO U20'
        if self.isGardolo or self.isUnder20:
            dateData = gameData.xpath('.//td[@class="risTr1P"]/font')
            # Se è presente la data, la partita non è ancora stata giocata,
            # posso quindi salvarla su calendar
            if len(dateData) > 0:
                self.futureGame = True
                data = re.fullmatch('(?P<day>\d\d)/(?P<month>\d\d)/(?P<year>\d\d\d\d) - (?P<time>\d\d:\d\d)', dateData[0].text.strip())
                self.gameday = date(int(data.group('year')), int(data.group('month')), int(data.group('day')))
                self.time = time(*map(int, data.group('time').split(':')))
                if self.isUnder20:
                    if self.isGardolo:
                        self.league += ['Under 20']
                    else:
                        self.league = ['Under 20']
            else:
                self.futureGame = False
                self.result = gameData.xpath('.//td[@class="risTr1P"]')[0].text.strip()
