import discord
import ivern.riot_api as riot_api
import ivern.utils as utils

from datetime import datetime
from discord.ext.commands import Bot
from ivern.riot_api import RiotAPI

bot = Bot(command_prefix='!')
token = ''  # Add in Discord app bot user token


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
        region = riot_api.REGION.get(str(api.default_region)).get('region')
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
            riot_api.REGION.get(str(region)).get('name'),
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
                if champion_mastery[i].get('championId', 0) == value.get('id'):
                    field_text += 'Level **{0}**: {1} ({2})\n'.format(
                        champion_mastery[i].get('championLevel'),
                        value.get('name'),
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
            match_history.get('matches')
        )
        field1_text = ''
        field2_text = ''
        for i in range(0, matches_to_display):
            match_details = api.get_match_details_by_match_id(
                region,
                match_history.get('matches')[i].get('gameId')
            )
            for j in range(0, 6 if match_details.get('mapId') == 10 else 10):
                if summoner_id == match_details.get('participantIdentities')[j].get('player').get('summonerId'):
                    for key, value in champion_data.get('data').items():
                        if match_history.get('matches')[i].get('champion') == value.get('id'):
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
                                value.get('name'),
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


@bot.command(pass_context=True)
async def mastery(ctx, *args):
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
        region = riot_api.REGION.get(str(api.default_region)).get('region')
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
    embed_message = discord.Embed(
        color=utils.color,
        title='Champion Mastery',
        description='**{0}** ({1})\n[OP.GG]({2})'.format(
            summoner_name,
            riot_api.REGION.get(str(region)).get('name'),
            'https://{0}.op.gg/summoner/userName={1}'.format(
                region,
                sanitized_name)),
    )
    embed_message.set_footer(
        text=utils.get_positive_quote(),
        icon_url=utils.icon
    )
    champion_mastery = api.get_champion_mastery_by_summoner_id(region, summoner_id)
    if not champion_mastery:
        embed_message.add_field(
            name='Champion Mastery',
            value='No champions to display.',
            inline=False
        )
    else:
        champions_to_display = 20 if len(champion_mastery) >= 20 else len(champion_mastery)
        champion_data = api.get_static_champion_data()
        field1_text = ''
        field2_text = ''
        field3_text = ''
        for i in range(0, champions_to_display):
            for key, value in champion_data.get('data').items():
                if champion_mastery[i].get('championId', 0) == value.get('id'):
                    field1_text += 'Level **{0}**: {1}\n'.format(
                        champion_mastery[i].get('championLevel'),
                        value.get('name')
                    )
                    field2_text += '{0} {1}\n'.format(
                        '{:,}'.format(
                            champion_mastery[i].get('championPoints')
                        ),
                        '({0} until **{1}**)'.format(
                            '{:,}'.format(champion_mastery[i].get('championPointsUntilNextLevel')),
                            champion_mastery[i].get('championLevel') + 1
                        ) if champion_mastery[i].get('championLevel') < 5 else ''
                    )
                    field3_text += '{0} {1}\n'.format(
                        '~~Chest~~' if champion_mastery[i].get('chestGranted') else 'Chest',
                        '(**{0}** token{1})'.format(
                            champion_mastery[i].get('tokensEarned'),
                            '' if champion_mastery[i].get('tokensEarned') == 1 else 's'
                        ) if champion_mastery[i].get('championLevel') == 5 or champion_mastery[i].get(
                            'championLevel') == 6 else ''
                    )
        total_champion_level = 0
        total_champion_points = 0
        total_chest_granted = 0
        for champion in champion_mastery:
            total_champion_level += champion.get('championLevel')
            total_champion_points += champion.get('championPoints')
            total_chest_granted += 1 if champion.get('chestGranted') else 0
        embed_message.add_field(
            name='Champion',
            value=field1_text,
            inline=True
        )
        embed_message.add_field(
            name='Points',
            value=field2_text,
            inline=True
        )
        embed_message.add_field(
            name='Status',
            value=field3_text,
            inline=True
        )
        embed_message.add_field(
            name='Total Level',
            value='{0}/{1}'.format(
                '{:,}'.format(
                    total_champion_level
                ),
                '{:,}'.format(
                    len(champion_mastery) * 7
                )
            ),
            inline=True
        )
        embed_message.add_field(
            name='Total Points',
            value='{:,}'.format(
                total_champion_points
            ),
            inline=True
        )
        embed_message.add_field(
            name='Total Chests',
            value='{0}/{1}'.format(
                '{:,}'.format(
                    total_chest_granted
                ),
                '{:,}'.format(
                    len(champion_mastery)
                )
            ),
            inline=True
        )
    return await bot.send_message(
        ctx.message.channel,
        embed=embed_message
    )


@bot.command(pass_context=True)
async def history(ctx, *args):
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
        region = riot_api.REGION.get(str(api.default_region)).get('region')
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
        title='Match History',
        description='**{0}** ({1})\n[OP.GG]({2})'.format(
            summoner_name,
            riot_api.REGION.get(str(region)).get('name'),
            'https://{0}.op.gg/summoner/userName={1}'.format(
                region,
                sanitized_name)),
    )
    embed_message.set_footer(
        text=utils.get_positive_quote(),
        icon_url=utils.icon
    )
    matches_to_display = 7
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
            name='Matches',
            value='No matches to display.',
            inline=False
        )
        return await bot.send_message(
            ctx.message.channel,
            embed=embed_message
        )
    else:
        matches_to_display = matches_to_display if len(match_history.get('matches')) >= matches_to_display else len(
            match_history.get('matches')
        )
        champion_data = api.get_static_champion_data()
        match_id = []
        field1_text = ''
        field2_text = ''
        champion_last_played = ''
        total_wins = 0
        total_kills = 0
        total_deaths = 0
        total_assists = 0
        total_cs = 0
        total_cs_per_min = 0
        for i in range(0, matches_to_display):
            match_details = api.get_match_details_by_match_id(
                region,
                match_history.get('matches')[i].get('gameId')
            )
            match_id.append(
                match_history.get('matches')[i].get('gameId')
            )
            for j in range(0, 6 if match_details.get('mapId') == 10 else 10):
                if summoner_id == match_details.get('participantIdentities')[j].get('player').get('summonerId'):
                    for key, value in champion_data.get('data').items():
                        if match_history.get('matches')[i].get('champion') == value.get('id'):
                            if champion_last_played == '':
                                champion_last_played = value.get('key')
                            field1_text += '(**{0}**) {1} ({2})\n'.format(
                                i + 1,
                                riot_api.get_queue_name_by_queue_id(
                                    match_history.get('matches')[i].get('queue')
                                ),
                                utils.convert_time_to_ago_string(
                                    datetime.now() - datetime.fromtimestamp(match_details.get('gameCreation') / 1000.0)
                                )
                            )
                            field2_text += '**{0}**: {1} ({2}/{3}/{4})\n'.format(
                                'Victory' if match_details.get('participants')[j].get('stats').get('win') else 'Defeat',
                                value.get('name'),
                                match_details.get('participants')[j].get('stats').get('kills'),
                                match_details.get('participants')[j].get('stats').get('deaths'),
                                match_details.get('participants')[j].get('stats').get('assists')
                            )
                            total_wins += 1 if match_details.get('participants')[j].get('stats').get('win') else 0
                            total_kills += match_details.get('participants')[j].get('stats').get('kills')
                            total_deaths += match_details.get('participants')[j].get('stats').get('deaths')
                            total_assists += match_details.get('participants')[j].get('stats').get('assists')
                            total_cs += match_details.get('participants')[j].get('stats').get(
                                'totalMinionsKilled') + match_details.get('participants')[j].get('stats').get(
                                'neutralMinionsKilled')
                            total_cs_per_min += (
                                sum(
                                    match_details.get('participants')[j].get('timeline').get(
                                        'creepsPerMinDeltas').values()) / len(
                                    match_details.get('participants')[j].get('timeline').get(
                                        'creepsPerMinDeltas')
                                )
                            )
        embed_message.set_thumbnail(
            url='http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{0}.png'.format(
                champion_last_played
            )
        )
        embed_message.add_field(
            name='Match',
            value=field1_text
        )
        embed_message.add_field(
            name='Details',
            value=field2_text
        )
        embed_message.add_field(
            name='Cumulative Stats',
            value='**Total Games**: {0}\n**Total KDA**: {1}/{2}/{3}\n**Total Minions Killed**: {4}'.format(
                matches_to_display,
                total_kills,
                total_deaths,
                total_assists,
                '{0:.0f}'.format(
                    total_cs
                )
            )
        )
        embed_message.add_field(
            name='Per Game Stats',
            value='{0}W/{1}L (**{2}**%)\n{3}/{4}/{5} (**{6}** KDA)\n{7} (**{8}** per minute)'.format(
                total_wins,
                matches_to_display - total_wins,
                '{0:.1f}'.format(
                    100 * (total_wins / matches_to_display)
                ),
                '{0:.1f}'.format(
                    total_kills / matches_to_display
                ),
                '{0:.1f}'.format(
                    total_deaths / matches_to_display
                ),
                '{0:.1f}'.format(
                    total_assists / matches_to_display
                ),
                '{0:.1f}'.format(
                    ((total_kills + total_assists) / total_deaths)
                ),
                '{0:.1f}'.format(
                    total_cs / matches_to_display
                ),
                '{0:.1f}'.format(
                    total_cs_per_min / matches_to_display
                )
            )
        )
        message = await bot.send_message(
            ctx.message.channel,
            embed=embed_message
        )
        for i in range(0, matches_to_display):
            await bot.add_reaction(
                message=message,
                emoji=utils.numbered_reactions[i]
            )
        reaction = await bot.wait_for_reaction(
            user=ctx.message.author,
            timeout=45,
            emoji=utils.numbered_reactions,
            message=message
        )
        if reaction is None:
            await bot.clear_reactions(
                message=message
            )
        else:
            await bot.clear_reactions(
                message=message
            )
            embed_message = match(
                region,
                sanitized_name,
                match_id[utils.numbered_reactions.index(reaction.reaction.emoji)]
            )
            await bot.edit_message(
                message=message,
                embed=embed_message
            )


def match(*args):
    region = args[0]
    sanitized_name = args[1]
    match_id = args[2]
    api = RiotAPI()
    summoner = api.get_summoner_by_name(region, sanitized_name)
    summoner_name = summoner.get('name')
    summoner_id = summoner.get('id')
    embed_message = discord.Embed(
        color=utils.color,
        title='Match Details',
        description='**{0}** ({1})\n[OP.GG]({2})'.format(
            summoner_name,
            riot_api.REGION.get(str(region)).get('name'),
            'https://{0}.op.gg/summoner/userName={1}'.format(
                region,
                sanitized_name)),
    )
    embed_message.set_footer(
        text=utils.get_positive_quote(),
        icon_url=utils.icon
    )
    match_details = api.get_match_details_by_match_id(
        region,
        match_id
    )
    champion_data = api.get_static_champion_data()
    items_data = api.get_static_item_data()
    masteries_data = api.get_static_masteries_data(
        params={
            'masteryListData': 'masteryTree'
        }
    )
    runes_data = api.get_static_runes_data(
        params={
            'runeListData': 'basic'
        }
    )
    field1_text = ''
    field2_text = ''
    field3_text = ''
    field4_text = ''
    field5_text = ''
    participant_count = 6 if match_details.get('mapId') == 10 else 10
    team_damage_dealt = 0
    team_damage_taken = 0
    team_gold_earned = 0
    team_minions_killed = 0
    champion_played = ''
    enemy_champion_played = 0
    items = ''
    ferocity_tree = '**Ferocity**: '
    ferocity_count = 0
    cunning_tree = '**Cunning**: '
    cunning_count = 0
    resolve_tree = '**Resolve**: '
    resolve_count = 0
    mark = '**Marks**: '
    seal = '**Seals**: '
    glyph = '**Glyphs**: '
    quint = '**Quintessences**: '
    runes_count = 0
    for i in range(0, participant_count):
        if summoner_id == match_details.get('participantIdentities')[i].get('player').get('summonerId'):
            participant_id = match_details.get('participantIdentities')[i].get('participantId')
            champion_played = match_details.get('participants')[participant_id - 1].get('championId')
            for key, value in champion_data.get('data').items():
                if champion_played == value.get('id'):
                    champion_played = value.get('name')
                    break
            break
    for i in range(0, participant_count):
        if match_details.get('participants')[participant_id - 1].get('teamId') == match_details.get(
                'participants')[i].get('teamId'):
            team_damage_dealt += match_details.get('participants')[i].get('stats').get(
                'totalDamageDealtToChampions')
            team_damage_taken += match_details.get('participants')[i].get('stats').get(
                'totalDamageTaken')
            team_gold_earned += match_details.get('participants')[i].get('stats').get(
                'goldEarned')
            team_minions_killed += match_details.get('participants')[i].get('stats').get(
                'totalMinionsKilled')
        if str(
                match_details.get('participants')[participant_id - 1].get('timeline').get('lane')) == str(
                match_details.get('participants')[i].get('timeline').get('lane')) and str(
                match_details.get('participants')[participant_id - 1].get('timeline').get('role')) == str(
                match_details.get('participants')[i].get('timeline').get('role')) and participant_id - 1 != i:
            enemy_champion_played = match_details.get('participants')[i].get('championId')
            for key, value in champion_data.get('data').items():
                if enemy_champion_played == value.get('id'):
                    enemy_champion_played = value.get('name')
                    break
    field1_text += '**{0}** ({1})\n{2} ({3})\n**{4}** vs {5} ({6})\nLevel **{7}**: {8}/{9}/{10} ({11} CS)'.format(
        'Victory' if match_details.get('participants')[participant_id - 1].get('stats').get('win') else 'Defeat',
        utils.convert_game_duration_to_string(
            int(match_details.get('gameDuration'))
        ),
        riot_api.get_queue_name_by_queue_id(
            match_details.get('queueId')
        ),
        utils.convert_time_to_ago_string(
            datetime.now() - datetime.fromtimestamp(match_details.get('gameCreation')/1000.0)),
        champion_played,
        enemy_champion_played,
        match_details.get('participants')[participant_id - 1].get('timeline').get('lane').title(),
        match_details.get('participants')[participant_id - 1].get('stats').get('champLevel'),
        match_details.get('participants')[participant_id - 1].get('stats').get('kills'),
        match_details.get('participants')[participant_id - 1].get('stats').get('deaths'),
        match_details.get('participants')[participant_id - 1].get('stats').get('assists'),
        match_details.get('participants')[participant_id - 1].get('stats').get('totalMinionsKilled')

    )
    field2_text += '**Dealt**: {0}' \
                   '\n**Magic**: {1} (**{2}**%)' \
                   '\n**Physical**: {3} (**{4}**%)' \
                   '\n**True**: {5} (**{6}**%)' \
                   '\n**Team Share**: {7}%'.format(
                        '{:,}'.format(
                            match_details.get('participants')[participant_id - 1].get('stats').get(
                                'totalDamageDealtToChampions')
                        ),
                        '{:,}'.format(
                            match_details.get('participants')[participant_id - 1].get('stats').get(
                                'magicDamageDealtToChampions')
                        ),
                        '{:,.1f}'.format(
                            100 * (
                                match_details.get(
                                    'participants')[participant_id - 1].get('stats').get(
                                    'magicDamageDealtToChampions') / match_details.get(
                                    'participants')[participant_id - 1].get('stats').get(
                                    'totalDamageDealtToChampions')
                            )
                        ),
                        '{:,}'.format(
                            match_details.get('participants')[participant_id - 1].get('stats').get(
                                'physicalDamageDealtToChampions')
                        ),
                        '{:,.1f}'.format(
                            100 * (
                                match_details.get(
                                    'participants')[participant_id - 1].get('stats').get(
                                    'physicalDamageDealtToChampions') / match_details.get(
                                    'participants')[participant_id - 1].get('stats').get(
                                    'totalDamageDealtToChampions')
                            )
                        ),
                        '{:,}'.format(
                            match_details.get('participants')[participant_id - 1].get('stats').get(
                                'trueDamageDealtToChampions')
                        ),
                        '{:,.1f}'.format(
                            100 * (
                                match_details.get(
                                    'participants')[participant_id - 1].get('stats').get(
                                    'trueDamageDealtToChampions') / match_details.get(
                                    'participants')[participant_id - 1].get('stats').get(
                                    'totalDamageDealtToChampions')
                            )
                        ),
                        '{:,.1f}'.format(
                            100 * (
                                match_details.get(
                                    'participants')[participant_id - 1].get('stats').get(
                                    'totalDamageDealtToChampions') / team_damage_dealt
                            )
                        )
                    )
    field3_text += '**Taken**: {0}' \
                   '\n**Magic**: {1} (**{2}**%)' \
                   '\n**Physical**: {3} (**{4}**%)' \
                   '\n**True**: {5} (**{6}**%)' \
                   '\n**Team Share**: {7}%'.format(
                        '{:,}'.format(
                            match_details.get('participants')[participant_id - 1].get('stats').get(
                                'totalDamageTaken')
                        ),
                        '{:,}'.format(
                            match_details.get('participants')[participant_id - 1].get('stats').get(
                                'magicalDamageTaken')
                        ),
                        '{:,.1f}'.format(
                            100 * (
                                match_details.get('participants')[participant_id - 1].get('stats').get(
                                    'magicalDamageTaken') /
                                match_details.get('participants')[participant_id - 1].get('stats').get(
                                    'totalDamageTaken')
                            )
                        ),
                        '{:,}'.format(
                            match_details.get('participants')[participant_id - 1].get('stats').get(
                                'physicalDamageTaken')
                        ),
                        '{:,.1f}'.format(
                            100 * (
                                match_details.get('participants')[participant_id - 1].get('stats').get(
                                    'physicalDamageTaken') /
                                match_details.get('participants')[participant_id - 1].get('stats').get(
                                    'totalDamageTaken')
                            )
                        ),
                        '{:,}'.format(
                            match_details.get('participants')[participant_id - 1].get('stats').get(
                                'trueDamageTaken')
                        ),
                        '{:,.1f}'.format(
                            100 * (
                                match_details.get('participants')[participant_id - 1].get('stats').get(
                                    'trueDamageTaken') /
                                match_details.get('participants')[participant_id - 1].get('stats').get(
                                    'totalDamageTaken')
                            )
                        ),
                        '{:,.1f}'.format(
                            100 * (
                                match_details.get(
                                    'participants')[participant_id - 1].get('stats').get(
                                    'totalDamageTaken') / team_damage_taken
                            )
                        )
                    )
    field4_text += '**Lane**: {0} (**{1}** per minute)' \
                   '\n**Jungle**: {2}' \
                   '\n**Difference vs {3}**: {4} per minute' \
                   '\n**Team Share**: {5}%'.format(
                        '{:,}'.format(
                            match_details.get('participants')[participant_id - 1].get('stats').get(
                                'totalMinionsKilled')
                        ),
                        '{:,.1f}'.format(
                            sum(
                                match_details.get('participants')[participant_id - 1].get('timeline').get(
                                    'creepsPerMinDeltas').values()) / len(
                                match_details.get('participants')[participant_id - 1].get('timeline').get(
                                    'creepsPerMinDeltas')
                            )
                        ),
                        '{:,}'.format(
                            match_details.get('participants')[participant_id - 1].get('stats').get(
                                'neutralMinionsKilled')
                        ),
                        enemy_champion_played,
                        '{:,.1f}'.format(
                            sum(
                                match_details.get('participants')[participant_id - 1].get('timeline').get(
                                    'csDiffPerMinDeltas').values()) / len(
                                match_details.get('participants')[participant_id - 1].get('timeline').get(
                                    'csDiffPerMinDeltas')
                            )
                        ),
                        '{:,.1f}'.format(
                            100 * (
                                match_details.get('participants')[participant_id - 1].get('stats').get(
                                    'totalMinionsKilled') / team_minions_killed
                            )
                        )
                    )
    field5_text += '**Earned**: {0} (**{1}** per minute)\n**Spent**: {2}\n**Team Share**: {3}%'.format(
        '{:,}'.format(
            match_details.get('participants')[participant_id - 1].get('stats').get('goldEarned')
        ),
        '{:,.1f}'.format(
            sum(
                match_details.get('participants')[participant_id - 1].get('timeline').get(
                    'goldPerMinDeltas').values()) / len(
                match_details.get('participants')[participant_id - 1].get('timeline').get(
                    'goldPerMinDeltas')
            )
        ),
        '{:,}'.format(
            match_details.get('participants')[participant_id - 1].get('stats').get('goldSpent')
        ),
        '{:,.1f}'.format(
            100 * (
                match_details.get('participants')[participant_id - 1].get('stats').get('goldEarned') / team_gold_earned
            )
        )
    )
    if match_details.get('participants')[participant_id - 1].get('stats').get('item0') is not None:
        if match_details.get('participants')[participant_id - 1].get('stats').get('item0') != 0:
            items += items_data.get('data').get(
                str(match_details.get('participants')[participant_id - 1].get('stats').get('item0'))).get('name') + '\n'
    if match_details.get('participants')[participant_id - 1].get('stats').get('item1') is not None:
        if match_details.get('participants')[participant_id - 1].get('stats').get('item1') != 0:
            items += items_data.get('data').get(
                str(match_details.get('participants')[participant_id - 1].get('stats').get('item1'))).get('name') + '\n'
    if match_details.get('participants')[participant_id - 1].get('stats').get('item2') is not None:
        if match_details.get('participants')[participant_id - 1].get('stats').get('item2') != 0:
            items += items_data.get('data').get(
                str(match_details.get('participants')[participant_id - 1].get('stats').get('item2'))).get('name') + '\n'
    if match_details.get('participants')[participant_id - 1].get('stats').get('item3') is not None:
        if match_details.get('participants')[participant_id - 1].get('stats').get('item3') != 0:
            items += items_data.get('data').get(
                str(match_details.get('participants')[participant_id - 1].get('stats').get('item3'))).get('name') + '\n'
    if match_details.get('participants')[participant_id - 1].get('stats').get('item4') is not None:
        if match_details.get('participants')[participant_id - 1].get('stats').get('item4') != 0:
            items += items_data.get('data').get(
                str(match_details.get('participants')[participant_id - 1].get('stats').get('item4'))).get('name') + '\n'
    if match_details.get('participants')[participant_id - 1].get('stats').get('item5') is not None:
        if match_details.get('participants')[participant_id - 1].get('stats').get('item5') != 0:
            items += items_data.get('data').get(
                str(match_details.get('participants')[participant_id - 1].get('stats').get('item5'))).get('name') + '\n'
    if match_details.get('participants')[participant_id - 1].get('stats').get('item6') is not None:
        if match_details.get('participants')[participant_id - 1].get('stats').get('item6') != 0:
            items += items_data.get('data').get(
                str(match_details.get('participants')[participant_id - 1].get('stats').get('item6'))).get('name') + '\n'
    for key in match_details.get('participants')[participant_id - 1].get('masteries'):
        if masteries_data.get('data').get(str(key.get('masteryId'))).get('masteryTree') == 'Ferocity':
            ferocity_tree += '(**{0}**) {1} '.format(
                key.get('rank'),
                masteries_data.get('data').get(str(key.get('masteryId'))).get('name')
            )
            ferocity_count += int(key.get('rank'))
        elif masteries_data.get('data').get(str(key.get('masteryId'))).get('masteryTree') == 'Cunning':
            cunning_tree += '(**{0}**) {1} '.format(
                key.get('rank'),
                masteries_data.get('data').get(str(key.get('masteryId'))).get('name')
            )
            cunning_count += int(key.get('rank'))
        elif masteries_data.get('data').get(str(key.get('masteryId'))).get('masteryTree') == 'Resolve':
            resolve_tree += '(**{0}**) {1} '.format(
                key.get('rank'),
                masteries_data.get('data').get(str(key.get('masteryId'))).get('name')
            )
            resolve_count += int(key.get('rank'))
    for key in match_details.get('participants')[participant_id - 1].get('runes'):
        if runes_data.get('data').get(str(key.get('runeId'))).get('rune').get('type') == 'red':
            mark += '(**{0}**) {1} '.format(
                key.get('rank'),
                runes_data.get('data').get(str(key.get('runeId'))).get('name')
            )
            runes_count += 1
        elif runes_data.get('data').get(str(key.get('runeId'))).get('rune').get('type') == 'yellow':
            seal += '(**{0}**) {1} '.format(
                key.get('rank'),
                runes_data.get('data').get(str(key.get('runeId'))).get('name')
            )
            runes_count += 1
        elif runes_data.get('data').get(str(key.get('runeId'))).get('rune').get('type') == 'blue':
            glyph += '(**{0}**) {1} '.format(
                key.get('rank'),
                runes_data.get('data').get(str(key.get('runeId'))).get('name')
            )
            runes_count += 1
        elif runes_data.get('data').get(str(key.get('runeId'))).get('rune').get('type') == 'black':
            quint += '(**{0}**) {1} '.format(
                key.get('rank'),
                runes_data.get('data').get(str(key.get('runeId'))).get('name')
            )
            runes_count += 1
    for key, value in champion_data.get('data').items():
        if champion_played == value.get('name'):
            champion_played = value.get('key')
            break
    embed_message.set_thumbnail(
        url='http://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{0}.png'.format(
            champion_played
        )
    )
    embed_message.add_field(
        name='Match Breakdown',
        value=field1_text,
        inline=False
    )
    embed_message.add_field(
        name='Damage Breakdown',
        value=field2_text
    )
    embed_message.add_field(
        name='ᅠ',
        value=field3_text
    )
    embed_message.add_field(
        name='CS Breakdown',
        value=field4_text
    )
    embed_message.add_field(
        name='Gold Breakdown',
        value=field5_text
    )
    if not items:
        embed_message.add_field(
            name='Items',
            value='No items to display.',
            inline=False
        )
    else:
        embed_message.add_field(
            name='Items',
            value=items,
            inline=False
        )
    if ferocity_count == 0 and cunning_count == 0 and resolve_count == 0:
        embed_message.add_field(
            name='Masteries',
            value='No masteries to display.',
            inline=False
        )
    else:
        embed_message.add_field(
            name='Masteries',
            value='{0}-{1}-{2}\n{3}\n{4}\n{5}'.format(
                ferocity_count,
                cunning_count,
                resolve_count,
                ferocity_tree,
                cunning_tree,
                resolve_tree
            ),
            inline=False
        )
    if runes_count == 0:
        embed_message.add_field(
            name='Runes',
            value='No runes to display.',
            inline=False
        )
    else:
        embed_message.add_field(
            name='Runes',
            value='{0}\n{1}\n{2}\n{3}'.format(
                mark.replace('Greater Mark of ', ''),
                seal.replace('Greater Seal of ', ''),
                glyph.replace('Greater Glyph of ', ''),
                quint.replace('Greater Quintessence of ', '')
            ),
            inline=False
        )
    return embed_message


bot.run(token)
