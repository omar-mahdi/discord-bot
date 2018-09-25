import requests
import json

API_KEY = ''


def getPlayerId(playerName):
    # Request information
    url = 'https://fortnite-public-api.theapinetwork.com/prod09/users/id'
    headers = {'authorization': API_KEY}
    data = {'username': playerName}

    # Submit request
    request = requests.post(url, headers=headers, data=data)
    request = request.json()

    # Return user ID
    return request['uid']


def getPlayerStats(playerName):
    playerId = getPlayerId(playerName)

    url = 'https://fortnite-public-api.theapinetwork.com/prod09/users/public/br_stats'
    headers = {'authorization': API_KEY}
    data = {'user_id': playerId, 'platform': 'pc'}

    request = requests.post(url, headers=headers, data=data)
    request = request.json()

    return formatPlayerData(request)


def formatPlayerData(data):
    stats = data['stats']
    total = data['totals']
    output = """**Player:** {}
    **Total Wins:** {}
    **Total Kills:** {}
    **Total Games:** {}
    **Winrate:** {}%
    **K/D:** {}
    --
    **Solo Wins:** {}
    **Duo Wins:** {}
    **Squad Wins:** {}
    --
    **Solo Kills:** {}
    **Duo Kills:** {}
    **Squad Kills:** {}
    --
    **Solo Matches:** {}
    **Duo Matches:** {}
    **Squad Matches:** {}
    --
    """.format(data['username'], total['wins'], total['kills'], total['matchesplayed'], total['winrate'], total['kd'], stats['placetop1_solo'], stats['placetop1_duo'], stats['placetop1_squad'], stats['kills_solo'], stats['kills_duo'], stats['kills_squad'], stats['matchesplayed_solo'], stats['matchesplayed_duo'], stats['matchesplayed_squad'])

    return output


def getChallenges():
    url = 'https://fortnite-public-api.theapinetwork.com/prod09/challenges/get'
    headers = {'authorization': API_KEY, 'X-Fortnite-API-Version': 'v1.1'}
    data = {'season': 'current'}

    request = requests.post(url, headers=headers, data=data)
    request = request.json()

    return formatChallenges(request)


def formatChallenges(data):
    currentWeek = int(data['currentweek'])
    currentWeekIndex = currentWeek - 1
    challenges = data['challenges']
    currentChallenges = challenges[currentWeekIndex]
    output = 'Week {} Challenges:'.format(currentWeek)

    for challenge in currentChallenges['entries']:
        output += """
        **{}** x{} | {} :star:""".format(
            challenge['challenge'], challenge['total'], challenge['stars'])

    return output
