import credentials
from datetime import datetime, timedelta
from pytz import timezone

romeTimeZone = timezone('Europe/Rome')

class Service:
    def __init__(self):
        # Inizializzo il servizio di Google Calendar
        self.service = credentials.get_service()

        # Salvo l'id dei vari calendari
        calendars = self.service.calendarList().list().execute()
        self.calendar_ids = {}
        for item in calendars.get('items', []):
            self.calendar_ids[item['summary']] = item['id']

        # Prendo tutti gli eventi di quest'anno da Calendar per controllare eventuali
        # spostamenti di partite ed evitare doppioni
        self.remoteEvents = self.service.events().list(
            calendarId=self.calendar_ids['Partite'],
            timeMin=f'{datetime.today().isoformat("T")}Z').execute()['items']

    def saveGame(self, game):
        if game.futureGame:
            for league in game.league:
                cal_ids = [v for k, v in self.calendar_ids.items() if league in k] + [self.calendar_ids['Partite']]
                for cal_id in cal_ids:
                    if self.check(game, league, cal_id):
                        print('        Inserisco la partita nel calendario')
                        start = datetime.combine(game.gameday, game.time)
                        end = start + timedelta(minutes=90)
                        match = {
                            'summary': f'{league}: {game.teamA} vs {game.teamB}',
                            'location': game.place,
                            'description': league,
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
                        self.service.events().insert(calendarId=cal_id, body=match).execute()
                        print(game.teamA, game.teamB, game.gameday)

    def check(self, game, league, calendarId):
        timeMin = datetime.combine(game.gameday, game.time) + timedelta(minutes=89)
        timeMax = datetime.combine(game.gameday, game.time) + timedelta(minutes=1)
        summary = f'"{league}: {game.teamA} vs {game.teamB}"'
        # Controllo lower-bound
        eventsResult = self.service.events().list(
            calendarId=calendarId,
            q=summary,
            timeMax=romeTimeZone.localize(timeMax).isoformat('T')).execute()

        if len(eventsResult.get('items', [])) == 0:
            return True

        # Controllo upper-bound
        eventsResult = self.service.events().list(
            calendarId=calendarId,
            q=summary,
            timeMin=romeTimeZone.localize(timeMin).isoformat('T')).execute()

        if len(eventsResult.get('items', [])) == 0:
            return True
        return False

    def existCalendar(self, league):
        return len([v for k, v in self.calendar_ids.items() if league in k]) > 0

    def deleteGame(self, game):
        gameSummary = game['summary']
        calendarId = [v for k, v in self.calendar_ids.items() if game['description'] in k][0]
        
        # Per cancellare l'evento dal calendario specifico devo ricavarne l'id,
        # per cui devo fare una richiesta al suo calendario cercando il nome dell'evento
        # e data d'inizio
        gameInSpecificCalendar = self.service.events().list(
            calendarId=calendarId,
            q=f'"{gameSummary}"',
            orderBy='startTime',
            timeMin=game['start']['dateTime'],
            singleEvents=True
        ).execute()['items'][0]

        # Cancello la partita dal calendario specifico
        self.service.events().delete(
            calendarId=calendarId,
            eventId=gameInSpecificCalendar['id']
        ).execute()
        # Cancello la partita dal calendario generale 
        self.service.events().delete(
            calendarId=self.calendar_ids['Partite'],
            eventId=game['id']
        ).execute()
