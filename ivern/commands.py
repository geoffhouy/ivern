import ivern.riot_api as riot_api
import ivern.utils as utils
import discord

from discord.ext.commands import Bot
from ivern.riot_api import RiotAPI
from datetime import datetime

bot = Bot(command_prefix='!')
token = ''  # Add in Discord app ivern user token


@bot.event
async def on_ready():
    print(
        '{0}\n\nLogged in as {1} ({2}) on {3} servers\n'.format(
            '\"One day, I\'ll root in one place and be everywhere.\" - Ivern Bramblefoot',
            bot.user.name,
            bot.user.id,
            len(bot.servers)
        )
    )
    await bot.change_presence(game=discord.Game(name='League of Legends'))


@bot.command(pass_context=True)
async def profile(ctx, *args):
    if not args:
        embed_message = discord.Embed(
            color=utils.color,
            title='Error',
            description='No summoner name entered.'
        )
        embed_message.set_footer(
            text=utils.get_negative_quote(),
            icon_url=utils.icon
        )
        return await bot.send_message(
            ctx.message.channel,
            embed=embed_message
        )
    region = None
    for key in riot_api.REGION:
        if args[0].lower() == key:
            region = args[0].lower()
    sanitized_name = str(''.join(args if region is None else args[1:])).replace('_', '')
    api = RiotAPI()
    if region is None:
        region = riot_api.REGION[api.default_region]['region']
    summoner = api.get_summoner_by_name(region, sanitized_name)
    summoner_name = summoner.get('name')
    if summoner_name is None:
        embed_message = discord.Embed(
            color=utils.color,
            title='Error',
            description='Invalid summoner name entered.'
        )
        embed_message.set_footer(
            text=utils.get_negative_quote(),
            icon_url=utils.icon
        )
        return await bot.send_message(
            ctx.message.channel,
            embed=embed_message
        )
    summoner_id = summoner.get('id')
    account_id = summoner.get('accountId')
    embed_message = discord.Embed(
        color=utils.color,
        title='Profile',
        description='**{0}** ({1})\n[OP.GG]({2})'.format(
            summoner_name,
            riot_api.REGION[region]['name'],
            'https://{0}.op.gg/summoner/userName={1}'.format(
                region,
                sanitized_name)),
    )
    embed_message.set_thumbnail(
        url='http://avatar.leagueoflegends.com/{0}/{1}.png'.format(
            region,
            sanitized_name
        )
    )
    embed_message.set_footer(
        text=utils.get_positive_quote(),
        icon_url=utils.icon
    )
    league = api.get_league_by_summoner_id(region, summoner_id)
    if not league:
        embed_message.add_field(
            name='Ranked Stats',
            value='No stats to display.',
            inline=False
        )
    else:
        embed_message.add_field(
            name='Ranked Stats',
            value='**{0} {1}** ({2} LP)\n{3}W/{4}L (**{5}**%)'.format(
                league[0].get('tier').title(),
                league[0].get('rank'),
                league[0].get('leaguePoints'),
                league[0].get('wins'),
                league[0].get('losses'),
                '{0:.1f}'.format(
                    100*(league[0].get('wins') / (league[0].get('wins') + league[0].get('losses')))
                )
            )
        )
    champion_mastery = api.get_champion_mastery_by_summoner_id(region, summoner_id)
    if not champion_mastery:
        embed_message.add_field(
            name='Champion Mastery',
            value='No champions to display.',
            inline=False
        )
    else:
        champions_to_display = 5 if len(champion_mastery) >= 5 else len(champion_mastery)
        champion_data = api.get_static_champion_data()
        field_text = ''
        for i in range(0, champions_to_display):
            for key, value in champion_data.get('data').items():
                if champion_mastery[i].get('championId', 0) == value['id']:
                    field_text += 'Level **{0}**: {1} ({2})\n'.format(
                        champion_mastery[i].get('championLevel'),
                        value['key'],
                        '{:,}'.format(
                            champion_mastery[i].get('championPoints')
                        )
                    )
        embed_message.add_field(
            name='Champion Mastery',
            value=field_text,
            inline=False
        )
    matches_to_display = 5
    match_history = api.get_match_history_by_account_id(
        region,
        account_id,
        params={
            'beginIndex': '0',
            'endIndex': str(matches_to_display)
        }
    )
    if not match_history:
        embed_message.add_field(
            name='Match History',
            value='No matches to display.',
            inline=False
        )
    else:
        matches_to_display = matches_to_display if len(match_history.get('matches')) >= matches_to_display else len(
            match_history.get('matches'))
        field1_text = ''
        field2_text = ''
        for i in range(0, matches_to_display):
            match_details = api.get_match_details_by_match_id(
                region,
                match_history.get('matches')[i].get('gameId'))
            for j in range(0, 6 if match_details.get('mapId') == 10 else 10):
                if summoner_id == match_details.get('participantIdentities')[j].get('player').get('summonerId'):
                    for key, value in champion_data.get('data').items():
                        if match_history.get('matches')[i].get('champion') == value['id']:
                            field1_text += '{0} ({1})\n'.format(
                                riot_api.get_queue_name_by_queue_id(
                                    match_history.get('matches')[i].get('queue')
                                ),
                                utils.convert_time_to_ago_string(
                                    datetime.now() - datetime.fromtimestamp(match_details.get('gameCreation') / 1000.0)
                                )
                            )
                            field2_text += '**{0}**: {1} ({2}/{3}/{4})\n'.format(
                                'Victory' if match_details.get('participants')[j].get('stats').get('win') else 'Defeat',
                                value['key'],
                                match_details.get('participants')[j].get('stats').get('kills'),
                                match_details.get('participants')[j].get('stats').get('deaths'),
                                match_details.get('participants')[j].get('stats').get('assists')
                            )
        embed_message.add_field(
            name='Match History',
            value=field1_text
        )
        embed_message.add_field(
            name='ᅠ',
            value=field2_text
        )
    return await bot.send_message(
        ctx.message.channel,
        embed=embed_message
    )


bot.run(token)
