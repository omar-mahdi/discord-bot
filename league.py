import requests

API_KEY = ''
CHAMPION_API_KEY = ''


def getSummonerId(summonerName):
    url = 'https://euw1.api.riotgames.com/lol/summoner/v3/summoners/by-name/{}{}'.format(
        summonerName, API_KEY)
    request = requests.get(url)

    try:
        # Check if summoner name actually exists and then return their id, otherwise return false
        id = request.json()['id']
        return id
    except(KeyError):
        return False


def getSummonerMastery(summonerName):
    summonerId = getSummonerId(summonerName)

    if summonerId:
        url = 'https://euw1.api.riotgames.com/lol/champion-mastery/v3/champion-masteries/by-summoner/{}{}'.format(
            summonerId, API_KEY)
        request = requests.get(url)
        request = request.json()
        request = request[:5]  # Get top 5 champions
        # Set champion IDs to names instead of IDs
        champions = getChampionNames(request)
        output = ''
        # Format champions for discord
        for champion in champions:
            output += '\n**{}** Mastery Level {} — {} Points'.format(
                champion['championId'], champion['championLevel'], champion['championPoints'])
        return output


def getSummonerRank(summonerName):
    summonerId = getSummonerId(summonerName)
    if summonerId:
        url = 'https://euw1.api.riotgames.com/lol/league/v3/positions/by-summoner/{}{}'.format(
            summonerId, API_KEY)
        request = requests.get(url)
        request = request.json()
        return formatRanks(request)
    else:
        return 'Summoner could not be found!'


def formatRanks(request):
    # Default input is unranked in case the user doesn't have a ranked solo or ranked flex object
    solo = 'SOLO: **Unranked**'
    flex = 'FLEX: **Unranked**'

    # Check all leagues in the object and determine if thy're solo or flex
    for league in request:
        if league['queueType'] == 'RANKED_FLEX_SR':
            flex = 'FLEX: **{} {}**'.format(
                league['tier'], league['rank'], league['leaguePoints'])
        elif league['queueType'] == 'RANKED_SOLO_5x5':
            solo = 'SOLO: **{} {}**'.format(
                league['tier'], league['rank'], league['leaguePoints'])
    return solo + ' || ' + flex


def getGameSummoners(summonerName):
    summonerId = getSummonerId(summonerName)

    if summonerId:
        url = 'https://euw1.api.riotgames.com/lol/spectator/v3/active-games/by-summoner/{}{}'.format(
            summonerId, API_KEY)
        request = requests.get(url)
        request = request.json()

        # Return all players in the game
        return request['participants']
    else:
        return 'Summoner could not be found!'


def getSummonersRank(summoners):
    for summoner in summoners:
        rank = getSummonerRank(summoner['summonerName'])
        summoner['rank'] = rank
    return summoners


def getChampionId(championName):
    url = 'https://raw.githubusercontent.com/ngryman/lol-champions/master/champions.json'
    champions = requests.get(url)
    champions = champions.json()
    for champion in champions:
        if championName.lower() == champion['name'].lower():
            return champion['key']
    return False


def getChampionNames(summoners):
    url = 'https://raw.githubusercontent.com/ngryman/lol-champions/master/champions.json'
    champions = requests.get(url)
    champions = champions.json()
    # Loop through the champion list and matches the IDs with the summoner's champion
    for summoner in summoners:
        for champion in champions:
            if summoner['championId'] == int(champion['key']):
                summoner['championId'] = champion['name']
                break
    return summoners


def formatSummoners(summoners):
    output = '**Blue Team:**\n'
    for summoner in summoners[:5]:
        output += '{} || **{}** — {}\n'.format(summoner['summonerName'],
                                               summoner['championId'], summoner['rank'])
    output += '\n**Red Team:**\n'
    for summoner in summoners[5:]:
        output += '{} || **{}** — {}\n'.format(summoner['summonerName'],
                                               summoner['championId'], summoner['rank'])
    return output


def checkIfGameActive(summonerName):
    summonerId = getSummonerId(summonerName)
    if summonerId:
        url = 'https://euw1.api.riotgames.com/lol/spectator/v3/active-games/by-summoner/{}{}'.format(
            summonerId, API_KEY)
        request = requests.get(url)
        request = request.json()

        try:
            # Check if the game is active by checking if it has a players list
            request['participants']
            return True
        except (KeyError):
            return False
    else:
        return False


def lookupActiveGame(summonerName):
    if checkIfGameActive(summonerName):
        summoners = getGameSummoners(summonerName)
        summoners = getSummonersRank(summoners)
        summoners = getChampionNames(summoners)
        return formatSummoners(summoners)
    else:
        return 'Error!'


def getSummonerInfo(summonerName):
    if summonerName:
        output = ''
        output += getSummonerRank(summonerName)
        output += getSummonerMastery(summonerName)
        return output

#


def getChampionInfo(championName, role=''):
    championId = getChampionId(championName)

    if championId:
        url = 'http://api.champion.gg/v2/champions/{}?champData=hashes&api_key={}'.format(
            championId, CHAMPION_API_KEY)
        request = requests.get(url)
        request = request.json()

        if role:
            role = getRole(role)
            if role:
                for championRole in request:
                    if role == championRole['_id']['role']:
                        request = championRole
                        break
            else:
                return 'Invalid role specified! Possible roles are: **Top, Jgl, Mid, Bot, Support**'
        else:
            request = request[0]

        try:
            winrate = round(request['winRate'] * 100, 2)
        except(TypeError):
            return 'No data is available for this role!'

        items = request['hashes']['finalitemshashfixed']['highestCount']['hash']
        items = items[6:].split('-')
        items = getItemsInfo(items)

        firstItems = request['hashes']['firstitemshash']['highestCount']['hash']
        firstItems = firstItems[6:].split('-')
        firstItems = getItemsInfo(firstItems)

        skills = request['hashes']['skillorderhash']['highestCount']['hash']
        skills = skills[6:].split('-')

        runes = request['hashes']['runehash']['highestCount']['hash']
        runes = runes.split('-')
        runes = getRunesInfo(runes)

        role = translateRole(request['role'])

        return """**Role:** {}\n**Winrate:** {}%\n**Starting Items:** {}\n**Final Items:** {}\n**Rune Paths:** {}\n**Skill Order:** {}""".format(role, winrate, ', '.join(firstItems), ', '.join(items), ', '.join(runes), ' '.join(skills))
    else:
        return 'Invalid champion! Multi-word champion names should be enclosed in "quotes"!'


def getItemsInfo(items):
    url = 'http://ddragon.leagueoflegends.com/cdn/8.17.1/data/en_US/item.json'
    leagueItems = requests.get(url)
    leagueItems = leagueItems.json()['data']
    listOfItems = []
    for item in items:
        for leagueItem in leagueItems:
            if item == leagueItem:
                listOfItems.append(leagueItems[leagueItem]['name'])
                break

    return listOfItems


def getRunesInfo(runes):
    url = 'https://ddragon.leagueoflegends.com/cdn/8.17.1/data/en_US/runesReforged.json'
    leagueRunes = requests.get(url)
    leagueRunes = leagueRunes.json()
    listOfRunes = []
    paths = []
    paths.append(runes[0])
    paths.append(runes[5])

    for path in paths:
        for leaguePath in leagueRunes:
            if int(path) == leaguePath['id']:
                listOfRunes.append(leaguePath['name'])
                break

    return listOfRunes


def getRole(role):
    switch = {
        'support': 'DUO_SUPPORT',
        'bot': 'DUO_CARRY',
        'mid': 'MIDDLE',
        'top': 'TOP',
        'jgl': 'JUNGLE'
    }
    return switch.get(role.lower())


def translateRole(role):
    switch = {
        'DUO_SUPPORT': 'Support',
        'DUO_CARRY': 'Bot',
        'MIDDLE': 'Mid',
        'TOP': 'Top',
        'JUNGLE': 'Jungle'
    }
    return switch.get(role)
