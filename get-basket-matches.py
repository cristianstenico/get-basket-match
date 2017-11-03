from lxml import html
from datetime import datetime
from Game import Game
from pytz import timezone
from Service import Service
import requests
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

romeTimeZone = timezone('Europe/Rome')

localEvents = []

#Inizializzo classe di support per Google Calendar
service = Service()

# Scarico la homepage del sito Fip Trentino
home = requests.get('http://fip.it/risultati.asp?IDRegione=TN&com=RTN&IDProvincia=TN')

# Cerco i vari link delle categorie
for m in re.finditer('getCampionato\(\'RTN\', \'(?P<campionato>.+)\', \'(?P<fase>.+)\', \'(?P<codice>.+)\', (?P<andata>\d), (?P<turno>\d)\)', home.text):
    campionato = m.group('campionato')
    if campionato in squadre.keys() and service.existCalendar(squadre[campionato]):
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
                if game.isGardolo or game.isUnder20:
                    if game.futureGame:
                        localEvents.append(game)
                        service.saveGame(game)
                    else:
                        print(f'{game.teamA} - {game.teamB}: {game.result}')

# Controllo se ci sono partite su Calendar non più presenti sul sito Fip.
# In questo caso devo cancellarle da Calendar perché con tutta probabilità
# sono state spostate
for remoteEvent in service.remoteEvents:
    localEvent = [l for l in localEvents
        if remoteEvent['start']['dateTime'] == romeTimeZone.localize(datetime.combine(l.gameday, l.time)).isoformat('T') and remoteEvent['summary'] in [f'{league}: {l.teamA} vs {l.teamB}' for league in l.league]]
    if len(localEvent) == 0:
        service.deleteGame(remoteEvent)
        print(remoteEvent['summary'], remoteEvent['start']['dateTime'])
