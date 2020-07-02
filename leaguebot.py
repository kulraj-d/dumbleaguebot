import discord
import requests
from riotwatcher import LolWatcher, ApiError
import random

API_KEY = 'YOUR_LEAGUE_API'

def get_url(rank):
    if rank == 'IRON':
        return 'https://lolg-cdn.porofessor.gg/img/league-icons-v2/160/1-1.png'
    elif rank == 'BRONZE':
        return 'https://lolg-cdn.porofessor.gg/img/league-icons-v2/160/2-1.png'
    elif rank == 'SILVER':
        return 'https://lolg-cdn.porofessor.gg/img/league-icons-v2/160/3-1.png'
    elif rank == "GOLD":
        return 'https://lolg-cdn.porofessor.gg/img/league-icons-v2/160/4-1.png'
    elif rank == "PLATINUM":
        return 'https://lolg-cdn.porofessor.gg/img/league-icons-v2/160/5-1.png'
    elif rank == "DIAMOND":
        return 'https://lolg-cdn.porofessor.gg/img/league-icons-v2/160/6-1.png'
    elif rank == "MASTER":
        return 'https://lolg-cdn.porofessor.gg/img/league-icons-v2/160/7-1.png'
    elif rank == "GRANDMASTER":
        return 'https://lolg-cdn.porofessor.gg/img/league-icons-v2/160/8-1.png'
    else:
        return 'https://lolg-cdn.porofessor.gg/img/league-icons-v2/160/9-1.png'

def get_ranks(name, rank_type):
    lol_watcher = LolWatcher(API_KEY)
    my_region = 'na1'
    solo_dict = dict()
    flex_dict = dict()
    send_message = ""

    try:    
        response = lol_watcher.summoner.by_name(my_region, name)
        my_ranked_stats = lol_watcher.league.by_summoner(my_region, response['id'])

        for i in range(len(my_ranked_stats)):
            if my_ranked_stats[i]['queueType'] == 'RANKED_FLEX_SR' and (rank_type == "flex" or rank_type == "both"):
                flex_dict['tier'] = my_ranked_stats[i]['tier']
                flex_dict['rank'] = my_ranked_stats[i]['tier'] + " " + my_ranked_stats[i]['rank']
                flex_dict['points'] = my_ranked_stats[i]['leaguePoints']
                flex_dict['winrate'] = "***Wins***: {}\t\t ***Losses***: {}\t\t\n***WR***: {:0.2f}%".format(str(my_ranked_stats[i]['wins']), str(my_ranked_stats[i]['losses']),
                                                    my_ranked_stats[i]['wins']/(my_ranked_stats[i]['losses']+my_ranked_stats[i]['wins'])*100)
            elif my_ranked_stats[i]['queueType'] == 'RANKED_SOLO_5x5' and (rank_type == "solo" or rank_type == "both"):
                solo_dict['tier'] = my_ranked_stats[i]['tier']
                solo_dict['rank'] = my_ranked_stats[i]['tier'] + " " + my_ranked_stats[i]['rank']
                solo_dict['points'] = my_ranked_stats[i]['leaguePoints']
                solo_dict['winrate'] = "***Wins***: {}\t\t ***Losses***: {}\t\t\n***WR***: {:0.2f}%".format(str(my_ranked_stats[i]['wins']), str(my_ranked_stats[i]['losses']),
                                                    my_ranked_stats[i]['wins']/(my_ranked_stats[i]['losses']+my_ranked_stats[i]['wins'])*100)

    except ApiError as err:
        if err.response.status_code == 429:
            send_message = "Shit is down idk what to tell you"
        elif err.response.status_code == 404:
            send_message = 'Homie does not exist in NA :tired_face:'
        else:
            raise

    return (flex_dict, solo_dict, send_message)

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!dlb_commands'):
        await message.channel.send("Available commands are: !solo, !flex, !rank (for both), !whatismyq :100:")

    elif message.content.startswith('!whatismyq'):
            number = random.randint(1,2)
            if number == 2:
                await message.channel.send(file=discord.File('Yes.gif'))
            else:
                await message.channel.send(file=discord.File('No.gif'))

    else:
        name = message.content[6:]

        solo_dict = get_ranks(name, 'solo')[1]
        flex_dict = get_ranks(name, 'flex')[0]

        if len(solo_dict) > 0:
            solo_embed = discord.Embed(title = 'Ranked Solo', description = message.content[6:], color = discord.Color.blue())
            solo_embed.set_thumbnail(url = get_url(solo_dict['tier']))
            solo_embed.add_field(name = "Rank", value = solo_dict['rank'], inline = True)
            solo_embed.add_field(name = "LP", value = solo_dict['points'], inline = True)
            solo_embed.add_field(name = "Stats", value = solo_dict['winrate'], inline = False)

        if len(flex_dict) > 0:
            flex_embed = discord.Embed(title = 'Ranked Flex', description = message.content[6:], color = discord.Color.blue())
            flex_embed.set_thumbnail(url = get_url(flex_dict['tier']))
            flex_embed.add_field(name = "Rank", value = flex_dict['rank'], inline = True)
            flex_embed.add_field(name = "LP", value = flex_dict['points'], inline = True)
            flex_embed.add_field(name = "Stats", value = flex_dict['winrate'], inline = False)

        if message.content.startswith('!solo'):
            if get_ranks(name, 'solo')[2] != "":
                await message.channel.send(get_ranks(name, 'solo')[2])
            elif len(solo_dict) == 0:
                await message.channel.send("Summoner does not have a solo rank :100:")
            else:
                await message.channel.send(embed=solo_embed)
        elif message.content.startswith('!flex'):
            if get_ranks(name, 'flex')[2] != "":
                await message.channel.send(get_ranks(name, 'flex')[2])
            elif len(flex_dict) == 0:
                await message.channel.send("Summoner does not have a flex rank :100:")
            else:
                await message.channel.send(embed=flex_embed)
        elif message.content.startswith('!rank'):
            if len(solo_dict) > 0:
                await message.channel.send(embed=solo_embed)
            if len(flex_dict) > 0:
                await message.channel.send(embed=flex_embed)

client.run('YOUR_DISCORD_BOT_TOKEN')
