import requests

URL = {
    'base': 'https://{platform}.api.riotgames.com/lol/{url}',
    'champion': 'platform/v{version}/champions',
    'champion_mastery_by_summoner': 'champion-mastery/v{version}/champion-masteries/by-summoner/{summoner_id}',
    'league_by_summoner': 'league/v{version}/positions/by-summoner/{summoner_id}',
    'lol_status': 'status/v{version}/shard-data',
    'masteries_by_summoner': 'platform/v{version}/masteries/by-summoner/{summoner_id}',
    'match_by_account': 'match/v{version}/matchlists/by-account/{account_id}',
    'match_by_match': 'match/v{version}/matches/{match_id}',
    'runes_by_summoner': 'platform/v{version}/runes/by-summoner/{summoner_id}',
    'spectator_by_summoner': 'spectator/v{version}/active-games/by-summoner/{summoner_id}',
    'static_data': 'static-data/v{version}/{category}',
    'summoner_by_name': 'summoner/v{version}/summoners/by-name/{name}'
}
VERSION = {
    'champion': 3,
    'champion_mastery': 3,
    'league': 3,
    'lol_status': 3,
    'masteries': 3,
    'match': 3,
    'runes': 3,
    'spectator': 3,
    'static_data': 3,
    'summoner': 3,
}
REGION = {
    'br': {
        'name': 'Brazil',
        'platform': 'BR1',
        'region': 'br'
    },
    'eune': {
        'name': 'Europe Nordic & East',
        'platform': 'EUN1',
        'region': 'eune'
    },
    'euw': {
        'name': 'Europe West',
        'platform': 'EUW1',
        'region': 'euw'
    },
    'jp': {
        'name': 'Japan',
        'platform': 'JP1',
        'region': 'jp'
    },
    'kr': {
        'name': 'Korea',
        'platform': 'KR',
        'region': 'kr'
    },
    'lan': {
        'name': 'Latin America North',
        'platform': 'LA1',
        'region': 'lan'
    },
    'las': {
        'name': 'Latin America South',
        'platform': 'LA2',
        'region': 'las'
    },
    'na': {
        'name': 'North America',
        'platform': 'NA1',
        'region': 'na'
    },
    'oce': {
        'name': 'Oceania',
        'platform': 'OC1',
        'region': 'oce'
    },
    'ru': {
        'name': 'Russia',
        'platform': 'RU',
        'region': 'ru'
    },
    'tr': {
        'name': 'Turkey',
        'platform': 'TR1',
        'region': 'tr'
    }
}


class RiotAPI(object):

    def __init__(self):
        self._api_key = ''  # Add in Riot Games API key
        self.default_region = REGION['na']['region']  # Change region key to preferred region

    def _request(self, url, region, params={}):
        args = {'api_key': self._api_key}
        for key, value in params.items():
            if key not in args:
                args[key] = value
        response = requests.get(
            URL['base'].format(
                platform=REGION[self.default_region]['platform'] if region is None else REGION[region]['platform'],
                url=url
            ),
            params=args
        )
        print(response.url)
        return response.json()
