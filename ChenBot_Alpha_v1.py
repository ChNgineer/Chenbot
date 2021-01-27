#ChenBot_Alpha_v1.py

##########################################################################
#                           Imports and Setup                            #
##########################################################################

import os
import discord
import math
import io
import pickle
import time
from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
import threading
#import selenium
import random
#from PIL import Image
#import requests
#from io import BytesIO

#Bot connection related stuffs
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='//',intents=intents)

##########################################################################
#                               File Data                                #
##########################################################################

#List of focused people
focus_list = []

#Player class tracks player data
class Player:
    def __init__(self, id=None, name=None, position=None, skill=0, win_loss=[0,0], teamflag=0, gameflag=False, 陈民币=120, betflag=False, incometime=time.localtime(time.time())[7], investment=None):
        self.id = int(id)
        self.name = str(name)
        self.position = str(position)
        self.skill = skill
        self.win_loss = win_loss
        self.teamflag = teamflag
        self.gameflag = gameflag
        self.陈民币 = 陈民币
        self.betflag = betflag
        self.incometime = incometime
        self.investment = investment

    def __str__(self):
        return f'Name: {self.name}\nID: {self.id}\nRole: {self.position} | Rating: {self.skill} | W/L: {self.win_loss} | Active: {self.gameflag}\nNetworth: 陈¥{self.陈民币} | Current Investment: {self.investment}\n'
    def __repr__(self):
        return f'Name: {self.name}\nID: {self.id}\nRole: {self.position} | Rating: {self.skill} | W/L: {self.win_loss} | Active: {self.gameflag}\nNetworth: 陈¥{self.陈民币} | Current Investment: {self.investment}\n'

#Companies for Players to invest in
class Company:
    def __init__(self, name='', ticker='', CEO='', stock=0):
        self.name = name
        self.ticker = ticker
        self.CEO = CEO
        self.stock = stock

    def __str__(self):
        return f'{self.ticker} - {self.name} | CEO: {self.CEO} | Stock: 陈¥{self.stock}'

#Initialize player and currency logs
player_log = {}
company_log = {}
#Game state tracker
global game_state

#Load player log data from 'player_log.pkl'
if os.path.getsize('player_log.pkl') > 0:      
    with open('player_log.pkl', 'rb') as f:
        player_log = pickle.load(f)
        f.close()

#Load game_state from 'game_state.pkl'
if os.path.getsize('game_state.pkl') > 0:      
    with open('game_state.pkl', 'rb') as f:
        game_state = pickle.load(f)
        f.close()

#Load company data from 'company_log.pkl'
if os.path.getsize('company_log.pkl') > 0:      
    with open('company_log.pkl', 'rb') as f:
        company_log = pickle.load(f)
        f.close()

##########################################################################
#                               Functions                                #
##########################################################################

#Saves the player data to a .pkl file.
def save_data(infile, indict):
    f = open(infile,'wb')
    pickle.dump(indict,f)
    f.close()

#Updates a player's name when command is passed by them.
def update_player_name(ctx):
    if ctx.author.id not in player_log.keys():
        return
    player = player_log[ctx.author.id]
    if ctx.guild == None:
        player.name = ctx.author.name
        save_data('player_log.pkl', player_log)
        return
    if ctx.author.nick != None:
        player.name = ctx.author.nick
    else:
        player.name = ctx.author.name
    save_data('player_log.pkl', player_log)

#Partition helper functino for quicksort.
def partition(array, start, end):
    pivot = array[start]
    low = start + 1
    high = end
    while True:
        while low <= high and array[high] >= pivot:
            high = high - 1
        while low <= high and array[low] <= pivot:
            low = low + 1
        if low <= high:
            array[low], array[high] = array[high], array[low]
        else:
            break
    array[start], array[high] = array[high], array[start]
    return high

#General purpose quicksort function
def quick_sort(array, start, end):
    if start >= end:
        return
    p = partition(array, start, end)
    quick_sort(array, start, p-1)
    quick_sort(array, p+1, end)

#Player Debug print for troubleshooting
def player_debug_print(player):
    if type(player) == Player:
        print(player)
        print(f'Income Timer: {player.incometime} | Betflag: {player.betflag} | Teamflag: {player.teamflag}\n')
    else:
        print('type is not player.')

def checkTime():
    # This function runs periodically every 1 second
    threading.Timer(1, checkTime).start()

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    if(current_time == '13:00:00'):  # check if matches with the desired time
        channel = bot.get_channel(800520155422785556)
        payment = 0
        for company in company_log.values():
            RNG = random.randint(1,1000) #Normal distribution for odds partitioned by standard deviations 0.1%, 2.1%, 13.8%, 34.1%, 34.1%, 13.8%, 2.1%, 0.1%
            if RNG == 1:
                company.stock = rount(company.stock*0.25)
            elif RNG > 1 and RNG <= 22:
                company.stock = round(company.stock*0.5)
            elif RNG > 22 and RNG <= 160:
                company.stock = round(company.stock*0.6667)
            elif RNG > 160 and RNG <= 501:
                company.stock = round(company.stock*0.8333)
            elif RNG > 501 and RNG <= 842:
                company.stock = round(company.stock*1.2)
            elif RNG > 842 and RNG <= 978:
                company.stock = round(company.stock*1.5)
            elif RNG > 978 and RNG <= 999:
                company.stock = round(company.stock*2)
            elif RNG == 1000:
                company.stock = round(company.stock*4)
            for player in player_log.values():
                if player.investment != None:
                    if player.investment[0] == company.ticker:
                        player.陈民币 += int(player.investment[1])*int(company_log[player.investment[0]].stock)
                        player.investment = None

        save_data('company_log.pkl', company_log)
        save_data('player_log.pkl', player_log)

checkTime()

##########################################################################
#                               Bot Events                               #
##########################################################################

@bot.event
async def on_ready():
    QP = bot.get_guild(544390429672603658)
    print(f'{bot.user}: {bot.user.id}\n'
          f'Connection established at {time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())} to the following servers:')
    for server in bot.guilds:
        print(f'{server.name}: {server.id}')
    for player in player_log.values():
        if not hasattr(player, 'incometime'):
            setattr(player, 'incometime', time.localtime(time.time())[7])
        if not hasattr(player, 'betflag'):
            setattr(player, 'betflag', False)
        if not hasattr(player, 'investment'):
            setattr(player, 'investment', None)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content[3:len(message.content)-1] == '787765626658619434':
        await message.channel.send('SHINZOU WO SASAGEYO!')
        await message.channel.send('https://media1.tenor.com/images/6dc2e71b4fb1bac13e4e97ec8097f1f3/tenor.gif?itemid=8914717')

    if message.author.id == 153665086144118785:
        await message.add_reaction('\U0001F602')

    if message.content == 'ping':
        await message.channel.send('pong')

    if 'based' in message.content.lower():
        RNG = random.randint(1,2)
        if RNG == 1:
            await message.channel.send('based and red-pilled')

    if 'doublelift' in message.content.lower():
        await message.channel.send(
            'if doublelift has million number of fans i am one of them. '
            'if doublelift has ten fans i am one of them. '
            'if doublelift has no fans. '
            'that means i am no more on the earth. '
            'if world against doublelift, i am against the world. '
            'i love doublelift till my last breath... '
            'die hard fan of doublelift. '
            'Hit like if u think doublelift best & smart in the world')

    if 'toucan' in message.content:
        await message.channel.send(
            '░░░░░░░░▄▄▄▀▀▀▄▄███▄░░░░░░░░░░░░░░\n'
            '░░░░░▄▀▀░░░░░░░▐░▀██▌░░░░░░░░░░░░░\n'
            '░░░▄▀░░░░▄▄███░▌▀▀░▀█░░░░░░░░░░░░░\n'
            '░░▄█░░▄▀▀▒▒▒▒▒▄▐░░░░█▌░░░░░░░░░░░░\n'
            '░▐█▀▄▀▄▄▄▄▀▀▀▀▌░░░░░▐█▄░░░░░░░░░░░\n'
            '░▌▄▄▀▀░░░░░░░░▌░░░░▄███████▄░░░░░░\n'
            '░░░░░░░░░░░░░▐░░░░▐███████████▄░░░\n'
            '░░░░░le░░░░░░░▐░░░░▐█████████████▄\n'
            '░░░░toucan░░░░░░▀▄░░░▐█████████████▄ \n'
            '░░░░░has░░░░░░░░▀▄▄███████████████ \n'
            '░░░░░arrived░░░░░░░░░░░░█▀██████░░')

    if 'jojo' in message.content.lower():
            await message.channel.send(
                '⣿⣿⣿⣿⣿⣿⣿⡿⡛⠟⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n'
                '⣿⣿⣿⣿⣿⣿⠿⠨⡀⠄⠄⡘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n'
                '⣿⣿⣿⣿⠿⢁⠼⠊⣱⡃⠄⠈⠹⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n'
                '⣿⣿⡿⠛⡧⠁⡴⣦⣔⣶⣄⢠⠄⠄⠹⣿⣿⣿⣿⣿⣿⣿⣤⠭⠏⠙⢿⣿⣿⣿⣿⣿\n'
                '⣿⡧⠠⠠⢠⣾⣾⣟⠝⠉⠉⠻⡒⡂⠄⠙⠻⣿⣿⣿⣿⣿⡪⠘⠄⠉⡄⢹⣿⣿⣿⣿\n'
                '⣿⠃⠁⢐⣷⠉⠿⠐⠑⠠⠠⠄⣈⣿⣄⣱⣠⢻⣿⣿⣿⣿⣯⠷⠈⠉⢀⣾⣿⣿⣿⣿\n'
                '⣿⣴⠤⣬⣭⣴⠂⠇⡔⠚⠍⠄⠄⠁⠘⢿⣷⢈⣿⣿⣿⣿⡧⠂⣠⠄⠸⡜⡿⣿⣿⣿\n'
                '⣿⣇⠄⡙⣿⣷⣭⣷⠃⣠⠄⠄⡄⠄⠄⠄⢻⣿⣿⣿⣿⣿⣧⣁⣿⡄⠼⡿⣦⣬⣰⣿\n'
                '⣿⣷⣥⣴⣿⣿⣿⣿⠷⠲⠄⢠⠄⡆⠄⠄⠄⡨⢿⣿⣿⣿⣿⣿⣎⠐⠄⠈⣙⣩⣿⣿\n'
                '⣿⣿⣿⣿⣿⣿⢟⠕⠁⠈⢠⢃⢸⣿⣿⣶⡘⠑⠄⠸⣿⣿⣿⣿⣿⣦⡀⡉⢿⣧⣿⣿\n'
                '⣿⣿⣿⣿⡿⠋⠄⠄⢀⠄⠐⢩⣿⣿⣿⣿⣦⡀⠄⠄⠉⠿⣿⣿⣿⣿⣿⣷⣨⣿⣿⣿\n'
                '⣿⣿⣿⡟⠄⠄⠄⠄⠄⠋⢀⣼⣿⣿⣿⣿⣿⣿⣿⣶⣦⣀⢟⣻⣿⣿⣿⣿⣿⣿⣿⣿\n'
                '⣿⣿⣿⡆⠆⠄⠠⡀⡀⠄⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿\n'
                '⣿⣿⡿⡅⠄⠄⢀⡰⠂⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿')

    if ('choomba' and 'gf') in message.content.lower():
        await message.channel.send('https://cdn.discordapp.com/attachments/361987842156658688/793390958456209418/eq51t25y8u561.png')

    elif 'choomba' in message.content.lower():
        await message.channel.send(
            'Choomba\n\nNoun.\nA term used in the video game franchise \"Cyberpunk\"'
            'which refers to someone in a friendly way. Used in the same'
            'context as people calling friends \"bro\" or \"mate\".\n\n'
            '1.\"I need me a choomba-pilled gf.\" - ᵢₜ ₘₑ, ₘₐₛₛᵢ#7508\n'
            '2.\"It\'s like the N-word for latinos.\" - dvd#2368')

    if 'bruh' in message.content.lower():
        RNG = random.randint(1,2)
        if RNG == 1:
            await message.channel.send('https://cdn.discordapp.com/attachments/361987842156658688/797939191987437598/Bruh_zone.png')

    if '//unfocus' in message.content.lower():
        unfocus
    elif message.author.name in focus_list:
        await message.channel.send(f'{message.author.name}, get back to work')

    await bot.process_commands(message)
    
##########################################################################
#                             Focus Commands                             #
##########################################################################

@bot.command(name='focus', help='Get your head in the game.')
async def focus(ctx):
    if ctx.author.name in focus_list:
        await ctx.channel.send('You can\'t focus harder.')
        return
    focus_list.append(ctx.author.name)
    await ctx.channel.send('Focus mode engaged.')
    print(f'focus list: {focus_list}')

@bot.command(name='unfocus', help='Chill out, choomba.')
async def unfocus(ctx):
    if ctx.author.name not in focus_list:
        await ctx.channel.send('You were never focused in the first place.')
        return
    focus_list.remove(ctx.author.name)
    await ctx.channel.send(f'focus mode deactivated, welcome back {ctx.author.name}')
    print(f'focus list: {focus_list}')

##########################################################################
#                            Profile Commands                            #
##########################################################################

@bot.command(name='signup', help='{top,jg,mid,bot,sup,fill} Register for LoL in-houses.')
async def signup(ctx, *arg):
    if ctx.author.id in player_log.keys():
        await ctx.channel.send(f'You are already registered. Updating your role and name...')
        update_player_name(ctx)
        new_player = player_log[ctx.author.id]
        if arg == ():
            new_player.position = 'Spectator'
            new_player.gameflag = False
        elif 'top' in str(arg[0]).lower():
            new_player.position = 'Toplaner'
        elif 'jg' in str(arg[0]).lower() or 'jungle' in str(arg[0]).lower():
            new_player.position = 'Jungler'
        elif 'mid' in str(arg[0]).lower():
            new_player.position = 'Midlaner'
        elif 'bot' in str(arg[0]).lower() or 'adc' in str(arg[0]).lower():
            new_player.position = 'Botlaner'
        elif 'sup' in str(arg[0]).lower():
            new_player.position = 'Support'
        elif 'fill' in str(arg[0]).lower():
            new_player.position = 'Fill'
        else:
            await ctx.channel.send('That is not a real role. Please select one of {top, jg, mid, bot, sup, fill}.')
            return
    elif  arg == ():
        new_player = Player(id=ctx.author.id, position='Spectator')
    elif 'top' in str(arg[0]).lower():
        new_player = Player(id=ctx.author.id, position='Toplaner')
    elif 'jg' in str(arg[0]).lower() or 'jungle' in str(arg[0]).lower():
        new_player = Player(id=ctx.author.id, position='Jungler')
    elif 'mid' in str(arg[0]).lower():
        new_player = Player(id=ctx.author.id, position='Midlaner')
    elif 'bot' in str(arg[0]).lower() or 'adc' in str(arg[0]).lower():
        new_player = Player(id=ctx.author.id, position='Botlaner')
    elif 'sup' in str(arg[0]).lower():
        new_player = Player(id=ctx.author.id, position='Support')
    elif 'fill' in str(arg[0]).lower():
        new_player = Player(id=ctx.author.id, position='Fill')
    else:
        await ctx.channel.send('That is not a real role. Please select one of {top, jg, mid, bot, sup, fill}.')
        return
    if len(arg) == 2:
        await signup_secondary(ctx, new_player, arg[1])
    player_log[new_player.id] = new_player
    update_player_name(ctx)
    await ctx.channel.send(f'Thank you, {new_player.name}.'
                           f' You\'re now registered as a {new_player.position.lower()}.')
    if new_player.position == 'Spectator':
        await ctx.channel.send('Enjoy the show! You are not eligible to compete with //ready & //unready.')
    else:
        await ctx.channel.send('See you on the rift!')
    save_data('player_log.pkl', player_log)

async def signup_secondary(ctx, player, arg=None):
    if arg == None or player.position == 'Fill' or player.position == 'Spectator':
        return
    elif 'top' in arg.lower() and player.position != 'Toplaner':
        player.position += ', Toplaner'
    elif ('jg' in arg.lower() or 'jungle' in arg.lower()) and player.position != 'Jungler':
        player.position += ', Jungler'
    elif 'mid' in arg.lower() and player.position != 'Midlaner':
        player.position += ', Midlaner'
    elif ('bot' in arg.lower() or 'adc' in arg.lower()) and player.position != 'Botlaner':
        player.position += ', Botlaner'
    elif 'sup' in arg.lower() and player.position != 'Support':
        player.position += ', Support'
    elif 'fill' in arg.lower():
        player.position += ', Fill'
    else:
        await ctx.channel.send('That is not a real role. Please select one of {top, jg, mid, bot, sup, fill}.')
        return

@bot.command(name='roster', help='Prints the registered players of LoL in-houses.')
async def roster(ctx):
    if player_log == {}:
        await ctx.channel.send('No players registered, sign up with //sign-up {top, jg, mid, bot, sup}')
        return
    update_player_name(ctx)
    for player in player_log.values():
        await ctx.channel.send(f'{player}\n')

@bot.command(name='profile', help='Prints your LoL in-house info.')
async def profile(ctx):
    update_player_name(ctx)
    if ctx.author.id not in player_log.keys():
        await ctx.channel.send('You have no stats, you are not registered')
        return
    await ctx.channel.send(str(player_log[ctx.author.id]))

@bot.command(name='welfare', help='Daily login bonus of 陈¥120.')
async def welfare(ctx):
    if ctx.author.id not in player_log:
        await ctx.channel.send('You are not registered with ChenBot. You are not eligible to earn 陈¥.')
        return
    if player_log[ctx.author.id].incometime != time.localtime(time.time())[7]:
        player_log[ctx.author.id].陈民币 += 120
        player_log[ctx.author.id].incometime = time.localtime(time.time())[7]
        await ctx.channel.send(f'{player_log[ctx.author.id].name} earned 陈¥120.')
    else:
        await ctx.channel.send(f'You\'ve already used this today. Try again tomorrow.')
    save_data('player_log.pkl', player_log)

@bot.command(name='sink', help='{陈¥} Burn the 陈¥ before the cops come.')
async def sink(ctx, arg):
    if ctx.author.id not in player_log:
        await ctx.channel.send('You are not registered with ChenBot. You are not eligible to use 陈¥')
        return
    if arg.isnumeric() == True and player_log[ctx.author.id].陈民币 >= math.floor(float(arg)):
        player_log[ctx.author.id].陈民币 -= math.floor(float(arg))
        await ctx.channel.send(f'You got rid of 陈¥{arg}.')
        save_data('player_log.pkl', player_log)
        return
    await ctx.channel.send('Currency Rejected.')

@bot.command(name='pay', help='{@mention}{陈¥} Spare your choomba some change.')
async def donate(ctx, *arg):
    update_player_name(ctx)
    if len(arg) == 2 and (arg[0])[3:len(arg[0])-1].isnumeric() == True and arg[1].isnumeric() == True:
        player_id = int((arg[0])[3:len(arg[0])-1])
        amount = math.floor(float(arg[1]))
        if player_id != ctx.author.id and player_id in player_log.keys():
            if amount > 0 and amount <= player_log[ctx.author.id].陈民币:
                player_log[player_id].陈民币 += amount
                player_log[ctx.author.id].陈民币 -= amount
                save_data('player_log.pkl', player_log)
                await ctx.channel.send('Transaction complete. Pleasure doing business.\n'
                                       f'{player_log[ctx.author.id].name} sent {arg[1]} to {player_log[int(arg[0][3:len(arg[0])-1])].name}.')
                return
            await ctx.channel.send('Invalid funds for transaction detected.')
            return
        await ctx.channel.send('Invalid payment recipient detected.')
        return
    await ctx.channel.send('Invalid payment syntax.')

@bot.command(name='baltop', help='See who\'s got it better than you.')
async def baltop(ctx):
    money_list = []
    update_player_name(ctx)
    for player in player_log.values():
        money_list.append((player.陈民币, str(player.name)))
    quick_sort(money_list, 0, len(money_list)-1)
    money_list.reverse()
    await ctx.channel.send('Top Earners:\n'
                           f'1. {money_list[0][1]}: 陈¥{money_list[0][0]}\n'
                           f'2. {money_list[1][1]}: 陈¥{money_list[1][0]}\n'
                           f'3. {money_list[2][1]}: 陈¥{money_list[2][0]}\n'
                           f'4. {money_list[3][1]}: 陈¥{money_list[3][0]}\n'
                           f'5. {money_list[4][1]}: 陈¥{money_list[4][0]}\n')
    if ctx.author.id not in player_log.keys():
        return
    if player_log[ctx.author.id].陈民币 < money_list[4][0]: 
        await ctx.channel.send(f'.\n.\n.\n{money_list.index((player_log[ctx.author.id].陈民币, player_log[ctx.author.id].name)) + 1}.'
                           f'->You: 陈¥{player_log[ctx.author.id].陈民币}')

@bot.command(name='search', help='{@mention} Search for another user\'s profile.')
async def search(ctx, arg):
    if arg == None or not arg[3:len(arg)-1].isnumeric():
        await ctx.channel.send('Invalid search query detected.')
        return
    update_player_name(ctx)
    if int(arg[3:len(arg)-1]) in player_log.keys():
        await ctx.channel.send(str(player_log[int(arg[3:len(arg)-1])]))
        return
    await ctx.channel.send('User not found.')

@bot.command(name='fund', help='{@mention}{陈¥} Give +/- 陈¥. Mod Only.')
async def fund(ctx, *arg):
    if ctx.author.id != 177188338200084480 and ctx.author.id != 307663833915326464:
        await ctx.channel.send('Permission Denied. You\'re not a mod. Scram ya gonk!')
        return
    if str(arg[0][3:len(arg[0])-1]).isnumeric() and len(arg) == 2:
        if int(arg[0][3:len(arg[0])-1]) != ctx.author.id:
            update_player_name(ctx)
            if int(arg[0][3:len(arg[0])-1]) in player_log.keys():
                    player_log[int(arg[0][3:len(arg[0])-1])].陈民币 += int(arg[1])
                    save_data('player_log.pkl', player_log)
                    await ctx.channel.send('Transfer complete.\n'
                                           f'{player_log[int(arg[0][3:len(arg[0])-1])].name} received 陈¥{arg[1]}.')
                    return
            await ctx.channel.send('Target not found.')
            return
    await ctx.channel.send('Invalid transfer.')

@bot.command(name='kill', help='Dev Only. Not suspicious.')
async def kill(ctx, arg):
    if arg.isnumeric():
        if int(arg[3:len(arg)-1]) == 799096723334889492:
            await ctx.channel.send(f'I\'m sorry {ctx.author.mention}. I can\'t let you do that.')
            return
    await ctx.channel.send('Permission Denied')

@bot.command(name='invest', help='Buy shares on the stock market.\n'
             'Wait for company listing to complete in order to select company via ticker symbol.'
             ' Prompt for number of shares to purchase should follow.')
async def invest(ctx):
    update_player_name(ctx)
    def check1(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.upper() in company_log.keys()
    def check2(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.isnumeric()
    if player_log[ctx.author.id].investment != None:
        await ctx.channel.send('Slow down there choomba, you can only invest once per day.')
        return
    await ctx.channel.send(f'You have 陈¥{player_log[ctx.author.id].陈民币}\nLoading companies invest in, please be patient:')
    for company in company_log.values():
        await ctx.channel.send(company)
    await ctx.channel.send('Loading complete, invest with ticker symbol.')
    msg1 = await bot.wait_for('message', check=check1)
    if msg1.content.upper() in company_log.keys():
        await ctx.channel.send('How many shares would you like to purchase?')
        msg2 = await bot.wait_for('message', check=check2)
        if msg2.content.isnumeric():
            if int(msg2.content)*company_log[msg1.content.upper()].stock <= player_log[ctx.author.id].陈民币:
                player_log[ctx.author.id].陈民币 -= int(msg2.content)*company_log[msg1.content.upper()].stock
                player_log[ctx.author.id].investment = (company_log[msg1.content.upper()].ticker, msg2.content)
                await ctx.channel.send(f'{player_log[ctx.author.id].name} invested {int(msg2.content)*company_log[msg1.content.upper()].stock} into {company_log[msg1.content.upper()].name}.\nPleasure doing business.')
                save_data('player_log.pkl', player_log)
                return
            await ctx.channel.send('You do not have the liquid assets to purchase these shares.')
            return
        await ctx.channel.send('Invalid share quantity.')
        return
    await ctx.channel.send('There is no company by that ticker symbol.')

@bot.command(name='market', help='Displays stock market conditions.')
async def market(ctx):
    for company in company_log.values():
        await ctx.channel.send(company)

##########################################################################
#                            In-House Commands                           #
##########################################################################
#TODO: Emote Reactions
@bot.command(name='ready', help='Ready-check for the next LoL in-house game.')
async def ready(ctx):
    if ctx.author.id not in player_log.keys():
        await ctx.channel.send('You\'re not signed up to play.\n'
                               'Register with //signup {top, jg, mid, bot, sup, fill}.')
        return
    update_player_name(ctx)
    if (player_log[ctx.author.id]).gameflag != False:
        await ctx.channel.send(f'You were ready since {time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())}, {player_log[ctx.author.id].name}.')
        return
    if (player_log[ctx.author.id]).position == 'Spectator':
        await ctx.channel.send('You are a registered spectator. Use //signup {top, jg, mid, bot, sup, fill} '
                               'to pick a role eligible for in-house games.')
        return
    player_log[ctx.author.id].gameflag = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    await ctx.channel.send(f'{player_log[ctx.author.id].name} is ready to rumble.')
    save_data('player_log.pkl', player_log)

@bot.command(name='unready', help='Sit out the next LoL in-house game.')
async def unready(ctx):
    if ctx.author.id not in player_log.keys():
        await ctx.channel.send('You\'re not signed up to play.\n'
                               'Register with //signup {top, jg, mid, bot, sup, fill}.')
        return
    update_player_name(ctx)
    if (player_log[ctx.author.id]).gameflag == False:
        await ctx.channel.send(f'You were never ready in the first place, {player_log[ctx.author.id].name}.')
        return
    if (player_log[ctx.author.id]).position == 'Spectator':
        await ctx.channel.send('You are a registered spectator. Use //signup {top, jg, mid, bot, sup, fill} '
                               'to pick a role eligible for in-house games.')
        return
    player_log[ctx.author.id].gameflag = False
    await ctx.channel.send(f'{player_log[ctx.author.id].name} unreadied.')
    save_data('player_log.pkl', player_log)

@bot.command(name='dequeue', help='{@mention} Deactivate their ready-check for inhouses.')
async def dequeue(ctx, arg):
    if int(arg[3:len(arg)-1]) in player_log.keys():
        if player_log[int(arg[3:len(arg)-1])].gameflag != False:
            player_log[int(arg[3:len(arg)-1])].gameflag = False
            await ctx.channel.send(f'{player_log[int(arg[3:len(arg)-1])].name} dequeued.')
            save_data('player_log.pkl', player_log)
            return
        await ctx.channel.send(f'{player.name} is not queued.')
        return
    await ctx.channel.send('No active user by that name has been found')

@bot.command(name='randraft', help='Makes random in-house teams.')
async def random_draft(ctx):
    QP = bot.get_guild(544390429672603658)
    Red_role = QP.get_role(613953536320864256)
    Blue_role = QP.get_role(613953419602034696)
    active_players = []
    Blue_team = []
    Red_team = []
    global game_state
    if game_state == True:
        await ctx.channel.send('Game in progress, why are you trying to make a new one?.\n'
                               'Go watch your boys on the rift!\n'
                               'Alternatively end the game with //endmatch {none}.\n'
                               'WARNING: STATS FOR CANCELLED GAMES WILL NOT BE TRACKED.')
        return
    player_list = list(player_log.values())
    for player in player_list:
        if player.gameflag != False:
            active_players.append(player)
    if len(active_players) < 10:
        await ctx.channel.send('Not enough players eligible.\n'
                               'Register to play with //signup {top, jg, mid, bot, sup, fill}.\n'
                               'Registered? Ready up with //ready.')
        return
    elif len(active_players) > 10:
        await ctx.channel.send('Too many players are queued.\n'
                               'Step down with //unready.'
                               'Alternatively make someone else with //dequeue {@mention}.')
        return
    await ctx.channel.send('Shuffling players...\n'
                           'Bum bum be-dum bum bum be-dum bum...')
    random.shuffle(active_players)
    print(active_players)
    Blue_team = active_players[0:5]
    print(Blue_team)
    Red_team = active_players[5:10]
    print(Red_team)
    await ctx.channel.send('Blue Team:\n')
    for player in Blue_team:
        player_log[player.id].teamflag = 1
        for member in ctx.guild.members:
            if member.id == player.id:
                await member.add_roles(Blue_role)
        await ctx.channel.send(f'{player.name}\n')
    await ctx.channel.send('Red Team:\n')
    for player in Red_team:
        player_log[player.id].teamflag = 2
        for member in ctx.guild.members:
            if member.id == player.id:
                await member.add_roles(Red_role)
        await ctx.channel.send(f'{player.name}\n')
    game_state = True
    await ctx.channel.send('Team generation complete. Enjoy slaughtering each other for 15 to 50 minutes.')
    save_data('player_log.pkl', player_log)
    save_data('game_state.pkl', game_state)

@bot.command(name='reset', help='{stats, flags, all} Debugging tool. Dev only.')
async def reset(ctx, arg):
    if ctx.author.id != 177188338200084480:
        await ctx.channel.send('Permission Denied. You are not Chen. Scram ya gonk!')
        return
    QP = bot.get_guild(544390429672603658)
    Red_role = QP.get_role(613953536320864256)
    Blue_role = QP.get_role(613953419602034696)
    word_bank = []
    await ctx.channel.send('Resetting please be patient...\n'
                           'Bum bum be-dum bum bum be-dum bum...')
    if arg == 'flags' or arg == 'all':
        for player in player_log.values():
            player.gameflag = False
            player.teamflag = 0
        for member in QP.members:
            if member.id in player_log.keys():
                await member.remove_roles(Blue_role)
                await member.remove_roles(Red_role)
        game_state = False
        save_data('game_state.pkl', game_state)
    if arg == 'stats' or arg == 'all':
        for player in player_log.values():
            player.win_loss = [0,0]
            player.skill = 0
    save_data('player_log.pkl', player_log)
    
    await ctx.channel.send(f'{arg.capitalize()} for in-houses successfully reset')

@bot.command(name='force-flags', help='{@mention}{flag type}{flag value} Debugging tool. Dev only.')
async def force_flags(ctx, *arg):
    if ctx.author.id != 177188338200084480:
        await ctx.channel.send('Permission Denied. You are not Chen. Scram ya gonk!')
        return
    QP = bot.get_guild(544390429672603658)
    Red_role = QP.get_role(613953536320864256)
    Blue_role = QP.get_role(613953419602034696)
    if arg == None:
        await ctx.channel.send('Randomly selecting 10 players to force active game flags\n'
                           'Bum bum be-dum bum bum be-dum bum...')
        player_list = []
        for player in player_log.values():
            if player.position != 'Spectator':
                player_list.append(player)
        random.shuffle(player_list)
        print(player_list)
        i = 0
        while i < 10:
            player_log[player_list[i].id].gameflag = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            i += 1
        save_data('player_log.pkl', player_log)
        await ctx.channel.send('Forced conscription complete.\n'
                               f'{str(player_list[0:10])}')
        return

@bot.command(name='endmatch', help='{blue,red,none (winning team)}{rematch} Record in-house games.\n'
             'Record the winning team in the first arg or none if no team won. Second arg determines if '
             'teams, game state, and player activity flags are reset, or kept to play again (rematch).')
async def endmatch(ctx, *arg):
    global game_state
    if game_state == False:
        await ctx.channel.send('What are you ending? Your career? There is no game right now.')
        return
    QP = bot.get_guild(544390429672603658)
    Red_role = QP.get_role(613953536320864256)
    Blue_role = QP.get_role(613953419602034696)
    if len(arg) == 1:
        if arg[0] == 'blue':
            for player in player_log.values():
                if player.teamflag == 1:
                    player.win_loss[0] += 1
                if player.teamflag == 2:
                    player.win_loss[1] += 1
            save_data('player_log.pkl', player_log)
            await ctx.channel.send('Blue Team rewarded, Red Team penalized\n'
                                   'Teams disbanded, player queue cleared')
        elif arg[0] == 'red':
            for player in player_log.values():
                if player.teamflag == 1:
                    player.win_loss[1] += 1
                if player.teamflag == 2:
                    player.win_loss[0] += 1
            save_data('player_log.pkl', player_log)
            await ctx.channel.send('Blue Team penalized, Red Team rewarded\n'
                                   'Teams disbanded, player queue cleared')
        elif arg[0] == 'none':
            await ctx.channel.send('No Contest\nTeams disbanded.')
        else:
            await ctx.channel.send('Invalid argument, see //help endmatch.')
            return
        game_state = False
        save_data('game_state.pkl', game_state)
        for player in player_log.values():
            player.gameflag = False
            player.teamflag = 0
        for member in ctx.guild.members:
            await member.remove_roles(Blue_role)
            await member.remove_roles(Red_role)
        save_data('player_log.pkl', player_log)        
        return
    elif arg[1] == 'rematch':
        if arg[0] == 'blue':
            for player in player_log.values():
                if player.teamflag == 1:
                    player.win_loss[0] += 1
                if player.teamflag == 2:
                    player.win_loss[1] += 1
            await ctx.channel.send('Blue Team rewarded, Red Team penalized\n'
                                   'Teams kept for another round.')
            save_data('player_log.pkl', player_log)
            return
        elif arg[0] == 'red':
            for player in player_log.values():
                if player.teamflag == 1:
                    player.win_loss[1] += 1
                if player.teamflag == 2:
                    player.win_loss[0] += 1
            await ctx.channel.send('Blue Team penalized, Red Team rewarded\n'
                                   'Teams kept for another round.')
            save_data('player_log.pkl', player_log)
            return
        elif arg[0] == 'none':
            await ctx.channel.send('No Contest\nTeams kept for another round.')
            return
    await ctx.channel.send('Invalid argument, see //help endmatch.')
    return

@bot.command(name='readied', help='Displays number of readied players')
async def readied(ctx):
    player_list = []
    counter = 0
    await ctx.channel.send('Readied players:\n')
    for player in player_log.values():
        if player.gameflag != False:
            counter += 1
            player_list.append((player.gameflag, player.name, player.id, player.position))
            quick_sort(player_list, 0, len(player_list)-1)
    for player in player_list:
        await ctx.channel.send(f'{player[1]}: {player[3]}\n{player[2]} readied up on {player[0]}')
    await ctx.channel.send(f'{counter}/10 players are ready.')
    if counter < 10:
        await ctx.channel.send('Not enough players. Looks like the boys abandoned you.')
    elif counter == 10:
        await ctx.channel.send('This is where the fun begins.')
    else:
        await ctx.channel.send('Too many players. Use //unready or //dequeue {@mention}')

@bot.command(name='trade', help='{blueteam @mention}{redteam @mention}')
async def trade(ctx, arg1, arg2):
    QP = bot.get_guild(544390429672603658)
    Red_role = QP.get_role(613953536320864256)
    Blue_role = QP.get_role(613953419602034696)
    if ctx.author.id != 177188338200084480:
        await ctx.channel.send('Permission Denied. You are not Chen. Scram ya gonk!')
        return
    player1 = player_log[int(arg1[3:len(arg1)-1])]
    player2 = player_log[int(arg2[3:len(arg2)-1])]
    temp = player1.teamflag
    player1.teamflag = player2.teamflag
    player2.teamflag = temp
    save_data('player_log.pkl', player_log)
    for member in QP.members:
        if player1.id == member.id:
            await member.add_roles(Red_role)
            await member.remove_roles(Blue_role)
        if player2.id == member.id:
            await member.add_roles(Blue_role)
            await member.remove_roles(Red_role)
    await ctx.channel.send('Team transplant successful.')

##########################################################################
#                          Trading Card Commands                         #
##########################################################################
#TODO: Find out how to link images and gifs
#TODO: Make card class and attribues and methods

bot.run(TOKEN)