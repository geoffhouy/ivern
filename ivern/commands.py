import discord

from discord.ext.commands import Bot

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


bot.run(token)
