import random

color = 0x777409
icon = 'http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/Ivern.png'
numbered_reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']


def convert_time_to_ago_string(datetime):
    days = datetime.days
    hours, remainder = divmod(datetime.seconds, 3600)
    if days > 0:
        text = '{0} days ago'.format(days)
    else:
        if hours > 1:
            text = '{0} hours ago'.format(hours)
        else:
            text = 'Less than one hour ago'
    return text


def get_positive_quote():
    quote = [
        'My favorite color is spring.',
        'Live each day as if it\'s your first.',
        'The sunshine tastes so good today.',
        'Feels good to stretch the old beanstalks.',
        'What a wonderful day. Gooseberries would love it.',
        'Trees love tickling each other\'s branches.',
        'I find that the stranger life gets, the more it seems to make sense.',
        'Every river reaches the ocean in its own way.',
        'Ladybugs should really befriend inchworms.',
        'I follow only the sun! Eh, and sometimes a river. This one time, a scorpion.',
        'The cleverness of mushrooms always surprises me!',
        'Have an unusual day.',
        'Be grateful for this moment. And this one. Oh, and this one. Oh, and this one\'s good too!',
        'Nature gives so much more than it asks for in return.',
        'A gift from the forest.',
        'Given freely to those in need.',
        'Use this gift well.',
        'Don\'t play possum! Daisy hates possums!',
        'These are so much better than the mudloafers I\'ve been using.',
        'Oh, a feather-backed caterpillar!'
    ]
    return quote[random.randint(0, len(quote) - 1)]


def get_negative_quote():
    quote = [
        'Nature isn\'t always gentle.',
        'Trust me, you need this.',
        'It\'s okay, Gromp is a slow learner too.',
        'Huh. I can be thorny too.',
        'Some buds need a little push to blossom.',
        'Let me help you grow.',
        'The chameleons would be proud.',
        'Uh, the ferns did it.',
        'Who did that? It was me!',
        'Never trust a butterfly with a secret.',
        'Potatoes are always watching.',
        'I wonder what the ducks are plotting today.',
        'I am never lost in the wilderness... hehe, only in conversations.',
        'Don\'t fret, Blue. Moss builds character.',
        'Poor thing, who bent your antenna?',
        'Oh, you got me on that one!',
        'Malice is afoot.',
        'Do not linger here.',
        'Once in a blue leaf, the earthworm will best the robin.',
        'Never hurts to be carefully carefree.'
    ]
    return quote[random.randint(0, len(quote) - 1)]
