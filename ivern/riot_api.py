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

    def get_live_champion_data(self, region):
        return self._request(
            url=URL['champion'].format(
                version=VERSION['champion']
            ),
            region=region
        )

    def get_champion_mastery_by_summoner_id(self, region, summoner_id):
        return self._request(
            url=URL['champion_mastery_by_summoner'].format(
                version=VERSION['champion_mastery'],
                summoner_id=summoner_id
            ),
            region=region
        )

    def get_server_status(self, region):
        return self._request(
            url=URL['lol_status'].format(
                version=VERSION['lol_status'],
            ),
            region=region
        )

    def get_league_by_summoner_id(self, region, summoner_id):
        return self._request(
            url=URL['league_by_summoner'].format(
                version=VERSION['league'],
                summoner_id=summoner_id
            ),
            region=region
        )

    def get_masteries_by_summoner_id(self, region, summoner_id):
        return self._request(
            url=URL['masteries_by_summoner'].format(
                version=VERSION['masteries'],
                summoner_id=summoner_id
            ),
            region=region
        )

    def get_match_history_by_account_id(self, region, account_id, params={}):
        return self._request(
            url=URL['match_by_account'].format(
                version=VERSION['match'],
                account_id=account_id
            ),
            region=region,
            params=params
        )

    def get_match_details_by_match_id(self, region, match_id, params={}):
        return self._request(
            url=URL['match_by_match'].format(
                version=VERSION['match'],
                match_id=match_id
            ),
            region=region,
            params=params
        )

    def get_runes_by_summoner_id(self, region, summoner_id):
        return self._request(
            url=URL['runes_by_summoner'].format(
                version=VERSION['runes'],
                summoner_id=summoner_id
            ),
            region=region
        )

    def get_static_champion_data(self, params={}):
        return self._request(
            url=URL['static_data'].format(
                version=VERSION['static_data'],
                category='champions'
            ),
            region=None,
            params=params
        )

    def get_static_item_data(self, params={}):
        return self._request(
            url=URL['static_data'].format(
                version=VERSION['static_data'],
                category='items'
            ),
            region=None,
            params=params
        )

    def get_static_map_data(self, params={}):
        return self._request(
            url=URL['static_data'].format(
                version=VERSION['static_data'],
                category='maps'
            ),
            region=None,
            params=params
        )

    def get_static_masteries_data(self, params={}):
        return self._request(
            url=URL['static_data'].format(
                version=VERSION['static_data'],
                category='masteries'
            ),
            region=None,
            params=params
        )

    def get_static_profile_icon_data(self, params={}):
        return self._request(
            url=URL['static_data'].format(
                version=VERSION['static_data'],
                category='profile-icons'
            ),
            region=None,
            params=params
        )

    def get_summoner_by_name(self, region, name):
        return self._request(
            url=URL['summoner_by_name'].format(
                version=VERSION['summoner'],
                name=name
            ),
            region=region
        )
