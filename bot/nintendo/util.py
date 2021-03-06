from commons.config import SYSTEMS

from commons.keys import SWITCH
from commons.keys import TAG

NX_TAG = SYSTEMS[SWITCH][TAG]

alts = {
    '70010000001367': f'{NX_TAG}/AF3B',    # Doom
    '70010000004562': f'{NX_TAG}/AEYU2',   # NA: Johnny Turbo's Arcade: Gate Of Doom
    '70010000002341': f'{NX_TAG}/AB382',   # NA: NBA 2K18 Legend Edition
    '70010000002344': f'{NX_TAG}/AB383',   # NA: NBA 2K18 Legend Edition Gold
    '70010000012840': f'{NX_TAG}/AQ7P',    # NA: The Messenger
    '70010000001536': f'{NX_TAG}/AB382',   # JP: NBA 2K18 Legend Edition
    '70010000002346': f'{NX_TAG}/AB383',   # JP: NBA 2K18 Legend Edition Gold
    '70010000002608': f'{NX_TAG}/BAAN',    # JP: Mario + Rabbids Kingdom Battle
    '70010000012941': f'{NX_TAG}/AQ9F',    # EU: A Case of Distrust
    '70010000002023': f'{NX_TAG}/AM28',    # JP: Arena of Valor
    '70010000011429': f'{NX_TAG}/AQNJ',    # EU: Spider Solitaire F
    '70010000001345': f'{NX_TAG}/AENW',    # EU: SUPERBEAT: XONiC
    '70010000000854': f'{NX_TAG}/AN2B',    # EU: Let's Sing 2018
    '70010000009417': f'{NX_TAG}/AMUS',    # JP: Fallen Legion
    '70010000003655': f'{NX_TAG}/AK75',    # EU: Tricky Towers
    '70010000002022': f'{NX_TAG}/AM28',    # NA: Arena of Valor
    '70010000001641': f'{NX_TAG}/AHAB',    # NA: Party Planet
    '70010000007283': f'{NX_TAG}/AHAB2',   # EU: 30-in-1 Game Collection: Volume 1
    '70010000001906': f'{NX_TAG}/AHKT',    # EU: Timber Tennis: Versus
}

category_map = {
    'role-playing': 'rpg',
    'board_game': 'board game',
    'first_person_shooter': 'shooter',
    'puzzles': 'puzzle',
}


def get_game_id(nsuid, game_id):
    if nsuid in alts:
        return alts[nsuid]
    else:
        return game_id


def get_categories(categories):
    if type(categories) == str:
        categories = [categories.lower()]
    else:
        categories = [cat.lower() for cat in categories]

    return sorted([category_map.get(cat, cat) for cat in categories])

