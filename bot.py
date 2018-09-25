from league import getSummonerInfo, lookupActiveGame, getChampionInfo
from fortnite import getPlayerStats, getChallenges
from discord.ext import commands

bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def league(ctx, *args):
    if args[0] == 'active':
        if ctx.author.id == 276179145275211787:
            await ctx.send('Yes my lord...')
        else:
            await ctx.send('Retrieving data...')
        await ctx.send(lookupActiveGame(args[1]))
    elif args[0] == 'champion':
        if len(args) >= 3:
            await ctx.send(getChampionInfo(args[1], args[2]))
        else:
            await ctx.send(getChampionInfo(args[1]))
    else:
        await ctx.send(getSummonerInfo(args[0]))


@bot.command()
async def fortnite(ctx, arg):
    if arg == 'challenges':
        await ctx.send(getChallenges())
    else:
        if ctx.author.id == 276179145275211787:
            await ctx.send('Yes my lord...')
        else:
            await ctx.send('Retrieving data...')
        await ctx.send(getPlayerStats(arg))

bot.run('token')
