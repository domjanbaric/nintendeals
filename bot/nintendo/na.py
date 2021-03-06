import logging
import re
from datetime import datetime

import requests

from bot.nintendo.util import get_categories
from bot.nintendo.util import get_game_id

from commons.classes import Game

from commons.config import COUNTRIES
from commons.config import REGIONS
from commons.config import SYSTEMS

from commons.keys import ALIAS
from commons.keys import API
from commons.keys import NA
from commons.keys import REGION
from commons.keys import WEBSITE


LOG = logging.getLogger('nintendo.na')

AMERICA = REGIONS[NA]


def fetch_games(system, published_by_nintendo=False):
    additional = '&publisher=nintendo' if published_by_nintendo else ''

    start = 0
    limit = 200

    while True:
        if published_by_nintendo:
            LOG.info('Loading {} games published by nintendo (from {} to {})'.format(system, start, start + limit))
        else:
            LOG.info('Loading {} games (from {} to {})'.format(system, start, start + limit))

        url = AMERICA[API].format(system=SYSTEMS[system][ALIAS][NA], offset=start, limit=limit, additional=additional)
        response = requests.get(url)

        json = response.json()

        if not json.get('games', {}).get('game'):
            break

        for game in json['games']['game']:
            yield game

        start += limit


def _list_games(system, only_published_by_nintendo=False):
    for data in fetch_games(system, published_by_nintendo=only_published_by_nintendo):
        title = data.get('title', '')
        nsuid = data.get('nsuid')

        if nsuid in [None, 'HAC']:
            continue

        if not data.get('game_code'):
            # LOG.info('{} has no game id'.format(title))
            continue

        game_id = get_game_id(nsuid=nsuid, game_id=data.get('game_code'))

        game = Game(_id=game_id, system=system)

        game.titles[NA] = title
        game.nsuids[NA] = nsuid
        game.release_dates[NA] = datetime.strptime(data.get('release_date'), '%b %d, %Y')

        game.categories = get_categories(data.get('categories', {}).get('category', []))

        game.free_to_play = data.get('free_to_start', 'false') == 'true'

        if only_published_by_nintendo:
            game.published_by_nintendo = True

        try:
            game.number_of_players = int(re.sub('[^0-9]*', '', data.get('number_of_players', '0')))
        except:
            game.number_of_players = 0

        slug = data.get('slug')

        for country, details in COUNTRIES.items():
            if details[REGION] == NA and WEBSITE in details:
                game.websites[country] = details[WEBSITE].format(slug)

        yield game


def list_games(system):
    by_nintendo = []

    for game in _list_games(system, only_published_by_nintendo=True):
        by_nintendo.append(game.id)

        yield game

    for game in _list_games(system):
        if game.id in by_nintendo:
            continue

        yield game
