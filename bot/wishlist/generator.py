from db.mongo import GamesDatabase
from db.mongo import RedditDatabase
from db.mongo import WishlistDatabase

from bot.wishlist.constants import NO_WISHLIST
from bot.wishlist.constants import SEPARATOR
from bot.wishlist.constants import WISHLIST_EMPTY
from bot.wishlist.constants import REMOVE_URL

from commons.config import COUNTRIES
from commons.config import SYSTEMS

from commons.emoji import MINUS

from commons.keys import CURRENCY_CODE
from commons.keys import DIGITS
from commons.keys import ID
from commons.keys import FLAG

from commons.settings import USER_SUBREDDIT
from commons.settings import WEBSITE_URL

from commons.util import format_float


def build_wishlist(username):
    games_db = GamesDatabase()
    wishlist_db = WishlistDatabase()

    wishlist = wishlist_db.load(username)

    if not wishlist:
        return NO_WISHLIST

    if not len(wishlist.games):
        return WISHLIST_EMPTY

    games = {
        game.id: game
            for game in games_db.load_all(filter={ID: {'$in': list(wishlist.games.keys())}})
    }

    rows = []

    for wishlisted_game in wishlist.games.values():
        game = games.get(wishlisted_game.id)
        
        if not game:
            continue

        countries = wishlisted_game.countries

        country_list = [f'{COUNTRIES[country][FLAG]}' for country in countries if country in COUNTRIES]

        rows.append('{}|{}|{}'.format(
            game.title,
            ' '.join(country_list),
            f'[{MINUS}]({REMOVE_URL.format(game.id)})'
        ))

    rows.sort()

    content = [
        '',
        'Title | Countries | Actions',
        '--- | --- | :---: '
    ]

    content.extend(rows)

    return '\n'.join(content)


def generate_notification(sales_to_notify):
    rows = []

    for game, country_price, country, sale in sales_to_notify:
        title = game.title
        country = COUNTRIES[country]
        end_date = sale.end_date.strftime('%b %d')
        sale_price = format_float(sale.sale_price, country[DIGITS])
        full_price = format_float(country_price.full_price, country[DIGITS])

        if game.websites.get(country[ID]):
            title = '[{}]({})'.format(title, game.websites.get(country[ID]))

        rows.append(
            f'{title}|'
            f'*{end_date}*|'
            f'{country[FLAG]} **{country[CURRENCY_CODE]} {sale_price}** ~~{full_price}~~|'
            f'`{sale.discount}%`'
        )

    rows.sort()

    content = [
        'Title | Expiration | Price | %',
        '--- | --- | --- | :---: '
    ]

    content.extend(rows)
    content.append('')

    return '\n'.join(content)


def generate_header(username):
    return f'##Hi {username}!'


def generate_footer():
    reddit_db = RedditDatabase()

    footer = [
        '',
        f'Add games to your wishlist [HERE]({WEBSITE_URL}).',
        '',
        f'Check current deals on {USER_SUBREDDIT}:',
        ''
    ]

    for system in SYSTEMS:
        submission = reddit_db.load(f'{system}/{USER_SUBREDDIT}')

        if submission:
            footer.append(f'* [{system}]({submission.url.replace("https:", "") })')

    return '\n'.join(footer)


def build_response(content, username, include_wishlist=True):
    return '\n'.join(
        [
            generate_header(username),
            '',
            '',
            content,
            '___',
            build_wishlist(username) if include_wishlist else '',
            '___',
            generate_footer()
        ]
    )
