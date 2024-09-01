### General Imports ###
import os
import re
import sys
import pytz
import json
import time
import pickle
import random
import string
import asyncio
import subprocess
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta

### Discord Imports ###
import discord
from discord.ext import commands

### Local Imports ###
from vidya_words import vidya_words
from eternum_words import eternum_words
from powermanagement import prevent_standby

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='.', description="Gamemaster bot for Caribdis server", intents=intents)

# remove default help command
bot.remove_command('help')

# stay awake command for self-hosting
# macos
# subprocess.Popen('caffeinate')
# windows
prevent_standby()

#################
### Constants ###
################3

DEFAULT_QUESTIONS = 15 # Default amount of questions
MIN_QUESTIONS = 1 # Min amount of questions
MAX_QUESTIONS = 25 # Max amount of questions

NO_ANSWERS = ["n", "no", "nope"] # Answers that will add NO emoji
YES_ANSWERS = ["y", "yes", "yep", "yeah"] # Answers that will add YES emoji

# User IDs
WINGY_USER_ID = 206189166889926657
CANCHEZ_USER_ID = 283587623199571970
CLAIMANT_USER_ID = 1183302435217875045
CARI_USER_ID = 543504165779931157
PHIL_USER_ID = 549052137481437195
POND_USER_ID = 862875766832496671

DEF_SECONDS = 30

@bot.event
async def on_ready():
    # just prints to the console once we login
    print(f'We have logged in as {bot.user}')

##############
### Checks ###
##############

# These checks are used to control access to certain commands. General self explanatory by name

async def cooldown(ctx, seconds=DEF_SECONDS):
    # a check to see if a user is abusing a command
    cd_dict = load_cd(ctx)

    # bot testers don't get rate limited
    if ctx.message.author.id in [CLAIMANT_USER_ID, CANCHEZ_USER_ID]:
        return True

    if ctx.message.author.id in cd_dict.keys():
        last_cmd = cd_dict[ctx.message.author.id]['last_cmd']
        last_cmd_t = cd_dict[ctx.message.author.id]['last_time']

        # same command 30 secs apart
        if (last_cmd == ctx.command.name) and (datetime.now(tz=pytz.UTC) - last_cmd_t).total_seconds() < seconds:
            return False

    else:
        # defaults
        cd_dict[ctx.message.author.id] = {'last_time': datetime.now(tz=pytz.UTC), 'last_cmd': 'cmd'}

    cd_dict[ctx.message.author.id]['last_cmd'] = ctx.command.name
    cd_dict[ctx.message.author.id]['last_time'] = datetime.now(tz=pytz.UTC)
    save_cd(ctx, cd_dict)
    return True

async def can_do(ctx):
    # check for mods / super users
    users = load_mods(ctx)
    if ctx.author.id in users:
        return True
    else:
        return False

async def nancy_likes_you(ctx):
    # check for people Nancy likes, Nancy enjoyers only
    users = load_likes(ctx)

    # server boosters and nancy role havers automatically liked
    if 1251929518038585409 in [r.id for r in ctx.author.roles]:
        return True
    elif 919557542026297385 in [r.id for r in ctx.author.roles]:
        return True
    elif ctx.author.id in users or await can_do(ctx):
        return True
    else:
        return False

@bot.event
async def on_message(message):

    # load context
    ctx = await bot.get_context(message)
    m = message.content.lower()
    if ctx.guild == None:
        return

    # check for timeouts
    timeouts = load_pkl(ctx, 'timeout')
    if ctx.message.author.id in timeouts.keys() and m[1:].split(' ')[0] in [c.name for c in bot.commands]:
        if datetime.now(tz=pytz.UTC) > timeouts[ctx.message.author.id]:
            await ctx.send(f"{ctx.message.author.display_name} is free from timeout!")
            del timeouts[ctx.message.author.id]
            save_pkl(ctx, timeouts, 'timeout')
        else:
            await ctx.send("You are in still in timeout, sorry!")
            return

    # process bot_messages (if not in timeout)
    await bot.process_commands(message)

# always listening
@bot.listen('on_message')
async def always_on(message):

    # load context
    ctx = await bot.get_context(message)
    m = message.content.lower()
    if ctx.guild == None:
        return

    # don't respond to your own messages
    if message.author == bot.user:
        return

    # Nancy says hello
    if 'hi mommy' in message.content.lower() or 'hello mommy' in message.content.lower() and ':' not in message.content:
        await send_image_embed(ctx, "./images/", "wave.gif", text="Hiii Sweetie!")
        return

    # Luna says hello
    if 'hi luna' in message.content.lower() or 'hello luna' in message.content.lower() and ':' not in message.content:
        await send_image_embed(ctx, "./images/", "luna_wave.gif", text="Oh Nancy this one is for me. Hi!")
        return

    # blush when someone tells you you did a good job
    if message.content.lower().startswith('good bot'):
        if await nancy_likes_you(ctx):
            await send_image_embed(ctx, "./images/", "blush.png", text="Awww. Thanks sweetie.")
            return
        else:
            await send_image_embed(ctx, "./images/", "mad_mom.png", text="I don't know you, back off!")
            return

    # do naughty things to those who ask
    if message.content.lower().startswith('blow me'):
        if await nancy_likes_you(ctx):
            await message.delete()
            await send_image_embed(ctx, "./images/", "blowme.gif")
            return
        else:
            await message.delete()
            await send_image_embed(ctx, "./images/", "bat.png", text="I'll give you a blow to the head!")
            return

    # get sad when someone tells you you did a bad job
    if message.content.lower().startswith('bad bot'):
        if await nancy_likes_you(ctx):
            await unlike(ctx)

            await send_image_embed(ctx, "./images/", "sad.png", text="...")
            return
        else:
            await send_image_embed(ctx, "./images/", "mad_emp.webp", text="Like I give a fuck what you think")
            return

    """
    # slap people who say bad words
    if "fuck" == message.content.lower():
        await send_image_embed(ctx, "./images/", "slap.png", text="Language!")
        return
    """

    if "shut" in m and "up" in m and "nancy" in m:
        if await nancy_likes_you(ctx):
            await unlike(ctx)
            await message.channel.send(f"That's it no more nintendo for you mister, {message.author.mention}")
            return
        else:
            await message.channel.send(f"Jesus YOU shut the fuck up already!")
            return

    # send umbrellas when Wingy bleeds
    if message.author.id == WINGY_USER_ID and ("bleed" in message.content and "nose" in message.content and "tenor" in message.content):
        await message.channel.send("☔")
        await message.channel.send("Everyone get under the umbrella!")
        return

    # greet people you like, and ignore those you don't who @ you
    if bot.user.mentioned_in(message):
        if discord.MessageType.reply == message.type:
            return

        if message.content.startswith('.'):
            return

        # look for hellos
        if 'hi' in message.content.lower() or 'hello' in message.content.lower():
            await send_image_embed(ctx, "./images/", "wave.gif", text="Hiii Sweetie!")
            return

        if await nancy_likes_you(message):
            await send_image_embed(ctx, "./images/", "hello.png", text="Hiii Sweetie!")
        else:
            await send_image_embed(ctx, "./images/", "mad_mom.png", text="Excuse me, do I know you? Don't @ me")

@bot.command(description='List command categories')
async def cmd(ctx, cmdtype=None):

    if not cmdtype:
        # list each category of commands
        embed = discord.Embed()
        embed.add_field(name=".cmd", value="List all categories of commands, you are using it now!")
        embed.add_field(name=".cmdmod", value="All mod only commands")
        embed.add_field(name=".cmdinteract", value="All commands for interacting with other people")
        embed.add_field(name=".cmdgames", value="All commands for games you can play")
        embed.add_field(name=".cmdquestion", value="Commands for the 20 questions game")
        embed.set_footer(text="You can also use .cmd <subcommand> like '.cmd games'")

        await ctx.send("Here are all the different categories of commands!", embed=embed)

    elif cmdtype == 'mod':
        await cmdmod(ctx)
        return
    elif cmdtype == 'interact':
        await cmdinteract(ctx)
        return
    elif cmdtype == 'games':
        await cmdgames(ctx)
        return
    elif cmdtype == 'question':
        await cmdquestion(ctx)
        return
    else:
        await ctx.send(f"'{cmdtype}' is not a valid subcommand")

@bot.command(description='List all mod commands')
async def cmdmod(ctx):
    embed = discord.Embed()
    embed.add_field(name=".addmod", value="Add a new Nancy moderator")
    embed.add_field(name=".unmod", value="Remove a Nancy moderator")
    embed.add_field(name=".speak", value="Speak in a channel as Nancy")
    embed.add_field(name=".touchgrass", value="Timeout users from using Nancy")

    await ctx.send("Here are all the moderator commands", embed=embed)

@bot.command(description='List all interaction commands')
async def cmdinteract(ctx):
    embed = discord.Embed()
    embed.add_field(name = ".crucify", value = "Crucify your enemies, long live the WRE")
    embed.add_field(name = ".spankhard", value = "Really show 'em how it's done")
    embed.add_field(name = ".pats", value = "Who has been good lately? Reward them")
    embed.add_field(name = ".like", value = "Ask Nancy to like someone, can only be done by people she already likes")
    embed.add_field(name = ".unlike", value = "Ask Nancy to not like someone, can only be done by people she already likes")
    embed.add_field(name = ".bday", value = "Wish a friend Happy Birthday!")
    embed.add_field(name = ".tongue", value = "Random render from Eternum with a tongue involved")
    embed.add_field(name = ".suss", value = "Call out suspicious behavior")
    embed.add_field(name = ".hugs", value = "Hug your friends!")
    embed.add_field(name = ".curse", value = "Curse evil comments")
    embed.add_field(name = ".ew", value = "Express disgust")
    embed.add_field(name = ".yes", value = "Agree with someone")
    embed.add_field(name = ".no", value = "Disagree with someone (cutely)")
    embed.add_field(name = ".tease", value = "Blow a raspberry")
    embed.add_field(name = ".begone", value = "Keep the thots off you")
    embed.add_field(name = ".confused", value = "When people are talking nonsense")
    embed.add_field(name = ".uncivil", value = "Call out uncivilized behavior")
    embed.add_field(name = ".report", value = "Report a bug in Nancy")

    await ctx.send("Here are all the interaction commands", embed=embed)

@bot.command(description='List all game commands')
async def cmdgames(ctx):
    embed = discord.Embed()
    embed.add_field(name = ".betteracro", value = "Play acro, but without dumb letters")
    embed.add_field(name = ".alleyman", value = "Play hangman with more categories!")

    await ctx.send("Here are all the game commands", embed=embed)

@bot.command(description="List Question game commands")
async def cmdquestion(ctx):
    embed = discord.Embed()
    embed.add_field(name=".qstart [number]", value="Start a game. Optionally write a number to specify amount of questions. Default is 15")
    embed.add_field(name=".qstart <number> bot", value="Start a game where Nancy will select a character and you will have to guess!")
    embed.add_field(name=".q <question>", value="Submit a question")
    embed.add_field(name=".qa <answer>", value="Answer current question (host only)")
    embed.add_field(name=".qs", value="Show current state of the game")
    embed.add_field(name=".qstop", value="Stop current game (host only)")
    embed.add_field(name=".qdiscard", value="Discard a question (host only)")
    embed.add_field(name=".guess", value="Guess the characters name!")
    embed.add_field(name=".qrules", value="Rules for questions and answers")
    embed.add_field(name=".qlist", value="List all questions the bot can answer")
    embed.add_field(name=".qshuffle", value="Shuffle question options")
    embed.add_field(name=".qstats", value="See your lifetime game stats")
    embed.add_field(name=".qleader", value="See wins leaderboard (categories: all, bot, human, host)")
    await ctx.send("Here are all Question game commands", embed=embed)

####################
### Mod Commands ###
####################

@bot.command(description="Add a mod")
@commands.check(can_do)
async def addmod(ctx):
    mod_list = load_mods(ctx)
    if len(ctx.message.mentions) == 0:
        await ctx.send('Who do you want to add as a mod?')
    elif len(ctx.message.mentions) == 1:
        if ctx.message.mentions[0].id in mod_list:
            await ctx.send(f"{ctx.message.mentions[0].name} is already a Nancy mod!")
        else:
            await ctx.send(f"Congrats {ctx.message.mentions[0].mention} you are now a Nancy mod!")
            mod_list.append(ctx.message.mentions[0].id)
            save_mods(ctx, mod_list)
    else:
        await ctx.send('I can only add one mod at a time')

@bot.command(description="Remove a mod")
@commands.check(can_do)
async def unmod(ctx):
    mod_list = load_mods(ctx)
    if len(ctx.message.mentions) == 0:
        await ctx.send('Who do you want to remove as a mod?')
    elif len(ctx.message.mentions) == 1:
        if ctx.message.mentions[0].id in mod_list:
            mod_list.remove(ctx.message.mentions[0].id)
            await ctx.send(f"{ctx.message.mentions[0].name} is no longer a Nancy mod!")
            save_mods(ctx, mod_list)
        else:
            await ctx.send(f"Can't remove someone who isn't a mod already silly")
    else:
        await ctx.send('I can only remove one mod at a time')

@bot.command(description="Have Nancy talk")
@commands.check(can_do)
async def speak(ctx):

    if len(ctx.message.channel_mentions) == 1:
        await ctx.message.delete()
        channel = ctx.message.channel_mentions[0]
        msg = '>'.join(ctx.message.content.split('>')[1:])
        await channel.send(msg)
    else:
        await ctx.send("Please specify a channel")

@bot.command(description="Timeout a user from using Nancy")
@commands.check(can_do)
async def touchgrass(ctx, user, minutes=10):
    timeouts = load_pkl(ctx, 'timeout')
    if len(ctx.message.mentions) == 0:
        await ctx.send('Who do you want to timeout?')
    elif len(ctx.message.mentions) == 1:
        if ctx.message.mentions[0].id in timeouts.keys():
            await ctx.send(f"{ctx.message.mentions[0].name} is already in timeout!")
        else:
            timeouts[ctx.message.mentions[0].id] = datetime.now(tz=pytz.UTC) + timedelta(minutes=minutes)
            await ctx.send(f"{ctx.message.mentions[0].name} is in timeout for {minutes} minutes!")
            save_pkl(ctx, timeouts, 'timeout')
    else:
        await ctx.send('I can only timeout one person at a time!')

############################
### Interaction Commands ###
############################

@bot.command(description='Attempt to ravage bathrobe Nancy as she deserves')
@commands.check(cooldown)
async def ravage(ctx):

    if ctx.channel.id not in [779873459756335104, 1269074244814377041]:
        await ctx.send("It's way too public here! (go to #bot-and-spam)")
        return

    # deny ravage attempts (unless they are lucky)
    n = random.randint(1,20)

    # punch if not liked
    if await nancy_likes_you(ctx):

        # 20% chance to actually ravage
        if n >= 17:
            await send_image_embed(ctx, "./images/", "ravage.gif", text="I'll take what I want and what I want is you!")
            return
        
        elif n == 1:
            await send_image_embed(ctx, "./images/", "king.png", text="An ogre blocked your ravage attempt!")
            return

        elif n == 2:    
            await send_image_embed(ctx, "./images/", "hugger.png", text="Should have had faster reflexes...")
            return

        else:
            await send_image_embed(ctx, "./images/", "bathrobe.png", text="There's no time silly!")
    else:
        await send_image_embed(ctx, "./images/", "punch.png", text="Back off creep!")

@bot.command(description='For uncooperative server users')
@commands.check(cooldown)
async def crucify(ctx):
    # meme from Eternum, @someone to crucify them like the leader of the ERE

    # need to mention exactly one person
    if len(ctx.message.mentions) == 0:
        await ctx.send('Who should we crucify today?')
    elif len(ctx.message.mentions) == 1:
        await send_image_embed(ctx, "./images/", "crucify.png", text=f"Maximo, crucify {ctx.message.mentions[0].mention}!")
    else:
        await ctx.send('I can only crucify one person at a time')

@bot.command(description='For extremely uncooperative server users part 2')
@commands.check(cooldown)
async def spankhard(ctx):
    # meme from Eternum / Cari's server, @someone to spank them like Dalia!

    if len(ctx.message.mentions) == 0:
        await ctx.send('Who deserves a spanking?')

    elif len(ctx.message.mentions) == 1:

        # catch people trying to spank Nancy
        if ctx.message.mentions[0] == bot.user:
            await send_image_embed(ctx, "./images/", "naughty.gif", text=f"{ctx.message.author.mention} you've been naughty for trying to spank Mommy, time out for you!")
            return

        n = random.randint(1,20)
        if n == 1 or 'opensesame' in ctx.message.content:
            await send_image_embed(ctx, "./images/", "alley.png", text="Shouldn't have taken that shortcut...")
            return
        else:
            n = random.choice([2,4])
            await send_image_embed(ctx, "./images/", f"spank{n}.gif", text=f"{ctx.message.author.mention} spanked {ctx.message.mentions[0].mention} even harder (and they liked it)!")
    else:
        await ctx.send('I can only spank one person at a time')

@bot.command(description='Just pats between friends')
@commands.check(cooldown)
async def pats(ctx):
    # meme from Eternum, @someone to pat them like Nova!

    # only pat exactly one person
    if len(ctx.message.mentions) == 0:
        await ctx.send('Who do you want to pat? Tag them with this command.')
    elif len(ctx.message.mentions) == 1:
        # unique react for patting Nancy
        if ctx.message.mentions[0] == bot.user:

            if await nancy_likes_you(ctx):
                await ctx.send("I'm a grown woman I don't need pats!")
                await asyncio.sleep(1)
                await ctx.send(". . .")
                await asyncio.sleep(1)
                await send_image_embed(ctx, "./images/", f"nancy_pat.gif", text="Ok... just a little more...")
                return
            else:
                await send_image_embed(ctx, "./images/", f"bat.png", text="How dare you try to touch me!")
                return

        n = random.randint(1,3)
        await send_image_embed(ctx, "./images/", f"pats{n}.gif", text=f"{ctx.message.author.mention} pat {ctx.message.mentions[0].mention} on the head!")
    else:
        await ctx.send('One at a time for pats please!')

@bot.command(description="Put someone on Nancy's good side")
@commands.check(nancy_likes_you)
async def like(ctx):
    like_list = load_likes(ctx)

    if len(ctx.message.mentions) == 0:
        await ctx.send('Who do you want to me to like?')
    elif len(ctx.message.mentions) == 1:
        if ctx.message.mentions[0].id in like_list:
            await ctx.send(f"I already like {ctx.message.mentions[0].display_name}!")
        else:
            await ctx.send(f"Oooh I definitely like {ctx.message.mentions[0].mention} now, they are a cutie!")
            like_list.append(ctx.message.mentions[0].id)
            save_likes(ctx, like_list)
    else:
        await ctx.send('I can only like one new person at a time')

@bot.command(description="Put someone on Nancy's bad side")
@commands.check(nancy_likes_you)
async def unlike(ctx):
    like_list = load_likes(ctx)
    if '.unlike' not in ctx.message.content:
        like_list.remove(ctx.message.author.id)
        await ctx.send(f"{ctx.message.author.display_name} you are a creep, leave me alone!")
        save_likes(ctx, like_list)
    elif len(ctx.message.mentions) == 0:
        await ctx.send("Who should I not like?")
    elif len(ctx.message.mentions) == 1:
        if ctx.message.mentions[0].id in like_list:
            like_list.remove(ctx.message.mentions[0].id)
            await ctx.send(f"{ctx.message.mentions[0].display_name} is a creep, leave me alone!")
            save_likes(ctx, like_list)
        else:
            await ctx.send(f"Can't unlike someone I don't already like silly")

    else:
        await ctx.send('I can only unlike one person at a time')

@bot.command(description='Wish your friends Happy Birthday')
@commands.check(cooldown)
async def bday(ctx, user, girl=None):
    # One of the Eternum girls wishes you a happy birthday
    ops = os.listdir('./birthdays')
    if not girl:
        choice = random.choice(ops)
    else:
        choice = [g for g in ops if girl.lower() in g]

        # make sure they picked a valid girl
        if len(choice) == 0:
            await ctx.send(f"{girl} is not a valid birthday option! Try again.")
            return
        else:
            choice = choice[0]

    # need to mention exactly one person
    if len(ctx.message.mentions) == 0:
        await ctx.send("Who's birthday is it? Tag them in this command")
    elif len(ctx.message.mentions) == 1:
        await send_image_embed(ctx, "./birthdays/", choice, text=f"Happy Birthday {ctx.message.mentions[0].display_name}! I got you a little something!")
    else:
        await ctx.send('Only one birthday wish at a time!')

@bot.command(description='Random tongue render')
@commands.check(cooldown)
async def tongue(ctx):

    # pick a random png
    p = Path('./tongue')
    ops = list(p.glob('*.png'))
    s = random.choice(ops)

    # set the image
    img = discord.File(s, filename="scene.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://scene.png")

    await ctx.send(f"Nyahh", file=img, embed=embed)

@bot.command(description='Random hug render')
@commands.check(cooldown)
async def hugs(ctx):

    # pick a random png
    p = Path('./hugs')

    if ctx.author.id == WINGY_USER_ID:
        ops = list(p.glob('*penny*'))
    else:
        ops = list(p.glob('*.png'))
    s = random.choice(ops)

    # set the image
    img = discord.File(s, filename="scene.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://scene.png")

    await ctx.send(f"Come here!", file=img, embed=embed)

@bot.command(description='Yes custom react')
@commands.check(cooldown)
async def yes(ctx):
    
    # delete and respond to og message if a reply
    reply = False
    await ctx.message.delete()
    if ctx.message.reference:
        reply = True

    await send_image_embed(ctx, "./images/", "yes.gif", "", reply)

@bot.command(description='No custom react')
@commands.check(cooldown)
async def no(ctx):
    
    # delete and respond to og message if a reply
    reply = False
    await ctx.message.delete()
    if ctx.message.reference:
        reply = True

    await send_image_embed(ctx, "./images/", "no.gif", "", reply)

@bot.command(description='Tease custom react')
@commands.check(cooldown)
async def tease(ctx):
    
    # delete and respond to og message if a reply
    reply = False
    await ctx.message.delete()
    if ctx.message.reference:
        reply = True

    await send_image_embed(ctx, "./images/", "tease.gif", "Thbbft", reply=True)

@bot.command(description='Begone custom react')
@commands.check(cooldown)
async def begone(ctx):
    
    # delete and respond to og message if a reply
    reply = False
    if ctx.message.reference:
        await ctx.message.delete()
        reply = True

    await send_image_embed(ctx, "./images/", "begone.png", text="BEGONE THOT!", reply=True)

@bot.command(description='Confused custom react')
@commands.check(cooldown)
async def confused(ctx):

    # delete and respond to og message if a reply
    reply = False
    if ctx.message.reference:
        await ctx.message.delete()
        reply = True

    await send_image_embed(ctx, "./images/", "confused.gif", text="You are making me dizzy...", reply=True)

@bot.command(description='Use for suspect behavior')
@commands.check(cooldown)
async def suss(ctx):
    n = random.randint(1,6)

    await send_image_embed(ctx, "./images/", f"suss{n}.gif")

@bot.command(description='Curse evil comments')
@commands.check(cooldown)
async def curse(ctx):

    # delete and respond to og message if a reply
    reply = False
    if ctx.message.reference:
        await ctx.message.delete()
        reply = True

    await send_image_embed(ctx, "./images/", "curse.png", "", reply)

@bot.command(description='Call out brutish behavior')
@commands.check(cooldown)
async def uncivil(ctx):

    # delete and respond to og message if a reply
    reply = False
    if ctx.message.reference:
        await ctx.message.delete()
        reply = True

    await send_image_embed(ctx, "./images/", "uncivilized.png", "Loutish. Mannerless. UNCIVILIZED", reply)

@bot.command(description='Express disgust')
@commands.check(cooldown)
async def ew(ctx):

    # delete and respond to og message if a reply
    reply = False
    if ctx.message.reference:
        await ctx.message.delete()
        reply = True

    await send_image_embed(ctx, "./images/", "ew.gif", "", reply)

@bot.command(description='Report a bug to bot creators')
@commands.check(cooldown)
async def report(ctx):

    # delete and respond to og message if a reply
    reply = False
    if ctx.message.reference:
        await ctx.message.delete()
        reply = True

    # get bot dev objects
    claim = await bot.fetch_user(CLAIMANT_USER_ID)
    canch = await bot.fetch_user(CANCHEZ_USER_ID)

    await ctx.send("Moshi moshi? A bug?! Ok I'll connect you.")
    await send_image_embed(ctx, "./images/", "moshi-moshi.png", f"Paging {canch.mention} and {claim.mention}", reply)

#####################
### Game Commands ###
#####################

@bot.command(description="An acro that doesn't suck")
@commands.max_concurrency(1)
async def betteracro(ctx):
    # acrophonbia from Nadeko, but removing the useless letters (z, q, x)
    # it might make sense to do other smart things like make letters appear
    # in line with their language frequency or similar

    if ctx.channel.id not in [779873459756335104, 1269074244814377041]:
        await ctx.send("It's way too public here! (go to #bot-and-spam)")
        return

    # all acros are 3-5 letters
    num_l = random.randint(3, 5)
    
    # remove bad letters
    ls = string.ascii_letters[:26]
    ls = ls.replace('z', '')
    ls = ls.replace('q', '')
    ls = ls.replace('x', '')

    # randomly select letters and send them to the channel
    selected = [random.choice(ls).upper() for i in range(num_l)]
    prompt = '.'.join(selected)
    embed = discord.Embed(title="Acrophobia (without dumb letters)")
    embed.add_field(name = f"Game started. Create a sentence with the following acronym: {prompt}", 
                    value = "You have 60 seconds to respond")
    await ctx.send(embed=embed)

    def check1(m):
        # the bot will wait for 60 seconds and filter responses based on this command
        # this one checks if the message is in the original channel and the answer
        # matches the acro prompt letters
        if m.channel.id == ctx.channel.id:
            answer = [s[0].upper() for s in m.content.split()]
            if answer == selected:
                return True
            else:
                return False
        else:
            return False

    # 60 second prompt loop
    answers = {}
    this_time = datetime.now(tz=pytz.UTC)
    while (datetime.now(tz=pytz.UTC) - this_time).total_seconds() < 60:
        
        try:
            # fetch messages that match the prompt
            m = await bot.wait_for('message', check=check1, timeout=5.0)
            
            # skip empty messages that timeout
            if m == None:
                continue

            # block dashes for combining words
            if '-' in m.content:
                await m.delete()
                await ctx.send(f"Hey look {m.author.display_name} tried to cheat! Their answer was: {m.content}")
                continue
            
            # don't let people answer twice
            if m.author.name in answers.keys():
                continue
            # save answers and delete from channel
            answers[m.author.name] = m.content
            await m.delete()
        except asyncio.TimeoutError:
            continue
        else:
            continue

    vote_map = {}
    num_ans = len(answers)
    # make sure there is at least one answer
    if num_ans == 0:
        await ctx.send("No one answered!")
        return
    else:
        # write the answers into an embed and save in a dict so we can retrieve the winner later
        embed = discord.Embed(title="Acrophobia Answers! You have 60 seconds to vote with a number!")
        for i, a in enumerate(answers.items()):
            embed.add_field(name = f"Number {i+1}:", 
                            value = f"{a[1]}")
            vote_map[i+1] = a
        await ctx.send(embed=embed)
    
    def check2(m):
        # the bot will wait for 60 seconds and filter responses based on this command
        # this one checks if the message is in the original channel and the answer
        # is an available number to vote
        if m.channel.id == ctx.channel.id:
            if not m.content.isdigit():
                return False
            elif int(m.content) in range(1, num_ans+1):
                return True
            else:
                return False
        else:
            return False

    # 60 second vote loop
    votes = {}
    this_time = datetime.now(tz=pytz.UTC)
    while (datetime.now(tz=pytz.UTC) - this_time).total_seconds() < 60:
        
        try:
            # fetch messages that are valid votes
            m = await bot.wait_for('message', check=check2, timeout=5.0)

            # skip empty messages that timeout
            if m == None:
                continue

            # don't let people vote twice
            if m.author.name in votes.keys():
                await ctx.send("You can't vote twice. Dumbass.")
                continue

            # don't let people vote for themselves
            if m.author.name == vote_map[int(m.content)][0]:
                await ctx.send("You can't vote for yourself. Dumbass.")
                continue

            # save votes and delete the vote
            votes[m.author.name] = m.content
            await m.delete()
            await ctx.send(f"{m.author.display_name} has voted!")
        except asyncio.TimeoutError:
            continue
        else:
            continue

    # make sure someone votes
    if len(votes) == 0:
        await ctx.send("No one voted, no winner!")
        return
    else:
        # find the most common vote and how many times it was voted
        win_num, count = Counter(votes.values()).most_common(1)[0]
        win_person = vote_map[int(win_num)]

        # declare the winner!
        embed = discord.Embed()
        embed.add_field(name = f"Winner: {win_person[0]} with {count} votes", value = f"Answer: {win_person[1]}")
        await ctx.send(embed=embed)

@bot.command(description="Hangman with more categories")
@commands.max_concurrency(1)
async def alleyman(ctx):
    # Like Nadeko's hangman, but with new categories
    
    if ctx.channel.id not in [779873459756335104, 1269074244814377041]:
        await ctx.send("It's way too public here! (go to #bot-and-spam)")
        return

    # block DM playing
    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send("Can't play in DMs, sorry!")
        return

    filename = "body.png"

    if '-' in ctx.message.content:
        category = ctx.message.content.split('-')[-1]
        if 'videogames' == category:
            word = random.choice(vidya_words)
        elif 'eternum' == category:
            word = random.choice(eternum_words)
        else:
            await ctx.send(f"{category} is not a valid alleyman category")
            return
    else:
        await ctx.send("Please pick a category you would like to use! (currently -eternum or -videogames)")
        return

    # Set out the rules
    special_chars = [' ', "'", '-', '.', '1', '2', '3', '4', 
                     '5', '6', '7', '8', '9', ':']
    spaces = ['\_' if l not in special_chars else l for l in word]

    img = discord.File(f"./alleyman/part0.png", filename=filename)
    embed = discord.Embed(title="Alleyman game started!")
    embed.set_image(url=f"attachment://{filename}")
    embed.add_field(name = "Word", value = "".join(spaces), inline=False)
    embed.add_field(name = "Guessed Letters", value = '', inline=False)
    await ctx.send(embed=embed, file=img)

    def check(m):
        # listen only for votes on the right channel and single letters
        if m.channel.id == ctx.channel.id:
            
            # allow full guesses
            if m.content.lower() == word.lower():
                return True
            
            msg = m.content
            if not msg.isalpha():
                return False
            elif len(msg) == 1:
                return True
            else:
                return False
        else:
            return False

    # 5 minute wait to finish the game
    win = False
    lose = False
    bad_guesses = []
    this_time = datetime.now(tz=pytz.UTC)
    while (datetime.now(tz=pytz.UTC) - this_time).total_seconds() < 300:
        
        try:
            m = await bot.wait_for('message', check=check, timeout=5.0)
            
            # skip empty messages that timeout
            if m == None:
                continue

            # skip already guessed letters
            if m.content.lower() in bad_guesses or m.content.lower() in spaces:
                continue

            # check for full correct answers
            if m.content.lower() == word.lower():
                win = True 
                spaces = [l for l in word]

            # check if letter in word
            letter_indices = [ma.start() for ma in re.finditer(m.content.lower(), word.lower())]
            if letter_indices and not win:

                # switch spaces to match actual word
                for ma in letter_indices:
                    spaces[ma] = word[ma]

                # keep going if not all letters found
                if '\_' not in spaces:
                    win = True

            elif not win:
                bad_guesses.append(m.content.lower())
                if len(bad_guesses) == 6:
                    lose = True
                    spaces = [l for l in word]

            # select message based on state
            if win:
                e_msg = f"{m.author.display_name} won!"
            elif lose:
                e_msg = f"{m.author.display_name} lost!"
            else:
                e_msg = f"{m.author.display_name} guessed the letter '{m.content.lower()}'!"

            # send embed
            img = discord.File(f"./alleyman/part{len(bad_guesses)}.png", filename=filename)
            embed = discord.Embed(title=e_msg)
            embed.set_image(url=f"attachment://{filename}")
            embed.add_field(name = "Word", value = "".join(spaces))
            embed.add_field(name = "Guessed Letters", value = ' '.join(bad_guesses))
            await ctx.send(embed=embed, file=img)

            # breakout if over
            if win or lose:
                break
            else:
                continue

        except asyncio.TimeoutError:
            continue
        else:
            continue

        # catch if times out
        if not win and not lose:
            await ctx.send("Time ran out! Better luck next time!")

#############################
### 20 Questions Commands ###
#############################

@bot.command(description="Rules for the question game")
async def qrules(ctx):
    embed = discord.Embed(title="Questions Game Rules")
    embed.add_field(name="1)", value="The character you pick must either be named or have a line in the game", inline=False)
    embed.add_field(name="2)", value="You can't ask questions about version numbers", inline=False)
    embed.add_field(name="3)", value="A Love Interest is one of the 7 main girls in the gallery screen (side girls do not count, including Calypso).", inline=False)
    embed.add_field(name="4)", value="An NPC is a character in Eternum that is not controlled by an Earth human (but they can still be people. Ex: Praetorian's are NPCs, so is Roach the horse in the Wild West Server).", inline=False)
    embed.add_field(name="5)", value="When playing in bot mode, the bot will answer certain questions as false unless it is explicitly stated in the game as true. Ex: We don't know if Professor Bundledore has kids, but he doesn't mention them so the bot will answer no", inline=False)
    embed.add_field(name="6)", value="When playing in bot mode and guessing, default to guessing the character's first name if we know it and their last name otherwise", inline=False)
    embed.add_field(name="7)", value="Some characters don't have names but are fun to guess. In these cases, guess what the game calls them in their dialoge (Ex: 'Granny' from the phone call in 0.1)", inline=False)
    await ctx.send(embed=embed)

@bot.command(description="Start Questions game")
@commands.cooldown(5, 1200, type=commands.BucketType.user)
async def qstart(ctx, max_questions=DEFAULT_QUESTIONS, host='human'):
    """Start Questions game if not started already by creating and saving json"""

    if ctx.channel.id not in [779873459756335104, 1269074244814377041]:
        await ctx.send("It's way too public here! (go to #bot-and-spam)")
        return

    # block DM playing
    if isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send("Can't play in DMs, sorry!")
        return

    question_game = load_question_game(ctx)
    if question_game:
        await ctx.send("Questions Game is already running!")
        return
    
    if not MIN_QUESTIONS <= max_questions <= MAX_QUESTIONS:
        await ctx.send(f"Specify a number between {MIN_QUESTIONS} and {MAX_QUESTIONS}!")
        return

    if host == 'bot':
        data, characters = load_20q_characters()
        question_game = {
            "host": bot.user.id,
            "host_name": bot.user.display_name,
            "questions": [],
            "max_questions": max_questions,
            "answer" : random.choice(characters),
            "data" : data,
            "asked" : [],
            "options" : [], 
            "shuffle" : False
        }
    elif host == 'human':
        question_game = {
            "host": ctx.message.author.id,
            "host_name": ctx.message.author.display_name,
            "questions": [],
            "max_questions": max_questions,
        }
    else:
        await ctx.send(f"{host} is not a valid host for 20 questions!")
        return

    save_question_game(ctx, question_game)
    embed = create_question_game_embed(question_game)

    # TODO Keep or remove - up to you
    embed.add_field(name=".q <question>", value="Submit a question")
    embed.add_field(name=".qa <answer>", value="Answer current question (host only)")
    embed.add_field(name=".qs", value="Show current state of the game")
    embed.add_field(name=".qstop", value="Stop current game (host only)")
    embed.add_field(name=".qdiscard", value="Discard a question (host only)")
    embed.add_field(name=".guess", value="Guess the characters name!")
    embed.add_field(name=".qlist", value="List all questions the bot can answer")
    embed.add_field(name=".qshuffle", value="Shuffle question options")
    await ctx.send(embed=embed)

    # For Nancy hosted games, send question options
    if host == 'bot':
        await q_nancy(ctx, question_game, question_game['questions'])

@bot.command(description="Stop 20 question game")
async def qstop(ctx, game_over=False, guess=False):
    """Stop Questions game if running by clearing json"""
    question_game = load_question_game(ctx)
    if not question_game:
        await ctx.send("Questions game is not running!")
        return
    
    # catch games with no questions or find the first asker
    empty_game = False
    first_asker = None
    if len(question_game['questions']) == 0:
        empty_game = True
    else:
        first_asker = question_game['questions'][0]['author_id']
    
    if ctx.message.author.id in (question_game["host"], first_asker) or await can_do(ctx) or game_over or guess or empty_game:

        # handle Nancy/Bot games
        answer = None
        nancy_game = False
        if question_game['host'] == bot.user.id:
            nancy_game = True
            answer = question_game['answer']

        # send embed and clear the game (and save a copy for stats)
        q_game = question_game
        embed = create_question_game_embed(question_game, game_over=game_over, is_cancelled=True, guess=guess)
        await ctx.send(embed=embed)
        question_game = {}

        save_question_game(ctx, question_game)

        if guess:

            # process stats for this game
            calc_qstats(ctx, q_game, guessed=True)

            await ctx.send("You guessed correctly. Nice!")
        elif game_over:

            # process stats for this game
            calc_qstats(ctx, q_game, guessed=False)

            await ctx.send("Your guess was wrong, game over!")

            # share the answer if it's a Nancy hosted game
            if nancy_game:
                await ctx.send(f"The correct answer was: {answer}")
        else:    
            await ctx.send("The Questions game is stopped!")
        
    else:
        await ctx.send("Only host or mods can stop the game!")

@bot.command(description="Submit a question")
async def q(ctx, q_option=None):
    """ Submit a question if don't have unanswered one already"""
    question_game = load_question_game(ctx)
    if not question_game:
        return
    
    questions = question_game["questions"]

    # don't allow questions if the previous question is unanswered
    if questions:
        if questions[-1]["answer"] == "":
            await ctx.send("One question at a time!")
            return

    # block questions if only guesses are allowed
    if len(questions) == question_game["max_questions"]:
        await ctx.send("Once questions are out you can only guess! Use .guess.")
        return False

    # catch questions for Nancy hosted games
    if question_game['host'] == bot.user.id:
        
        # make sure they sent a question selection
        if not q_option:
            await ctx.send("Please select a question option!")
            return

        # make sure integer
        if not q_option.isnumeric():
            await ctx.send(f"{q_option} is not a valid question. See all question with .qlist")

        # make sure question not asked already
        q_option = int(q_option)
        if q_option in question_game['asked']:
            await ctx. send(f"Question #{q_option} has already been asked!")
            return

        # make sure its a valid question identifier
        if q_option not in question_game['data'].keys():
            await ctx.send(f"{q_option} is not a valid question. See all question with .qlist")
            return

        # remove question from options
        question_game['options'] = [opt for opt in question_game['options'] if opt['id'] != q_option]

        # add results to game state
        new_question = question_game['data'][q_option]['question']
        answer = question_game['data'][q_option][question_game['answer']]
        question_game['asked'].append(q_option)

    else:
        new_question = ctx.message.content.split('.q')[-1].strip()
        answer = ""
    
    if not new_question:
        await ctx.send("Please write a question!")
        return

    question_dict = {
        "question": new_question,
        "answer": answer,
        "author": ctx.message.author.display_name,
        "author_id" : ctx.message.author.id,
        "guess": False
    }
    question_game["questions"].append(question_dict)
    save_question_game(ctx, question_game)
    
    # ask for the next quesiton in a Nancy hosted game
    if question_game['host'] == bot.user.id:
        # don't add question options if last question
        if not len(questions) == question_game["max_questions"]:
            await q_nancy(ctx, question_game, questions)
        else:
            embed = create_question_game_embed(question_game)
            await ctx.send(embed=embed)
    else:
        embed = create_question_game_embed(question_game)
        await ctx.send(embed=embed)

async def q_nancy(ctx, question_game, questions, shuffle=False):
    embed = create_question_game_embed(question_game)

    # remove asked questions
    q_opts = [question_game['data'][i] for i in range(1, max(question_game['data'].keys())+1) if i not in question_game['asked']]
    
    if shuffle:
        q_opts = random.sample(q_opts, 5)
        question_game['shuffle'] = True
    elif len(question_game['options']) == 4:
        # remove existing options
        opt_ids = [opt['id'] for opt in question_game['options']]
        new_opts = [opt for opt in q_opts if opt['id'] not in opt_ids]
        
        # add next question if unshuffled
        if not question_game['shuffle']:
            q_opts = question_game['options'] + [new_opts[0]]
        else:
            q_opts = question_game['options'] + [random.choice(new_opts)]
    elif len(question_game['options']) == 5:
        q_opts = question_game['options']
    else:
        q_opts = [q_opts[i] for i in range(5)]
    
    embed.add_field(name="Select a question option below", value="Respond with .q <number of question option>")
    for q in q_opts:
        embed.add_field(name=f"Question Option #{q['id']}", value=q['question'], inline=False)

    question_game['options'] = q_opts
    save_question_game(ctx, question_game)
    await ctx.send(embed=embed)

@bot.command(description="List all bot questions")
async def qlist(ctx):
    data, characters = load_20q_characters()
    embed = discord.Embed(title="All available questions (Part 1)")
    for i in range(1, max(data.keys())+1):
        embed.add_field(name=f"Question #{data[i]['id']}", value=data[i]['question'])

        if i == 25:
            break

    await ctx.send(embed=embed)

    embed = discord.Embed(title="All available questions (Part 2)")
    for j in range(i, max(data.keys())+1):
        embed.add_field(name=f"Question #{data[j]['id']}", value=data[j]['question'])

    await ctx.send(embed=embed)

@bot.command(description="Shuffle questions available to be asked")
async def qshuffle(ctx):
    question_game = load_question_game(ctx)

    if not question_game:
        return

    await q_nancy(ctx, question_game, question_game['questions'], True)

@bot.command(description="Answer a question")
async def qa(ctx):
    """ Answer a question if have unanswered"""
    question_game = load_question_game(ctx)
    if not question_game:
        return
    
    if ctx.message.author.id != question_game['host']:
        return
    
    questions = question_game["questions"]

    if questions and questions[-1]["answer"]:
        await ctx.send("You don't have active questions!")
        return
    
    last_question = questions[-1]
    
    answer = ctx.message.content.split('.qa')[-1].strip()
    
    if not answer:
        await ctx.send("Please write the answer!")
        return

    # end the game if guess is correct
    if last_question['guess'] and answer.lower() in YES_ANSWERS:
        await qstop(ctx, guess=True)
        return
    
    last_question["answer"] = answer
    question_game["questions"][-1] = last_question

    save_question_game(ctx, question_game)

    # end game if you are above amount of questions and allow guess as final
    if len(questions) > question_game["max_questions"]:
        await qstop(ctx, game_over=True)
    else:
        embed = create_question_game_embed(question_game)

        await ctx.send(embed=embed)

@bot.command(description="Show current state of Question game")
async def qs(ctx):
    """ Show current game status """
    question_game = load_question_game(ctx)
    embed = create_question_game_embed(question_game)

    if question_game['host'] == bot.user.id:
        await q_nancy(ctx, question_game, question_game['questions'])
        return

    await ctx.send(embed=embed)

@bot.command(description="Discard last question")
async def qdiscard(ctx):
    """ Discard last question """
    question_game = load_question_game(ctx)
    if not question_game:
        return
    
    if ctx.message.author.id != question_game['host']:
        await ctx.send("Only host can discard questions!")
        return
    
    questions = question_game["questions"]

    if not questions:
        await ctx.send("You don't have any questions to discard!")
        return

    question_game["questions"].pop()
    save_question_game(ctx, question_game)

    embed = create_question_game_embed(question_game)

    await ctx.send(embed=embed)

@bot.command(description="Guess the character")
async def guess(ctx):
    """ Submit a question if don't have unanswered one already"""
    question_game = load_question_game(ctx)
    if not question_game:
        return
    
    questions = question_game["questions"]

    if questions and questions[-1]["answer"] == "":
        await ctx.send("One guess at a time!")
        return

    new_question = ctx.message.content.split('.guess')[-1].strip()
    
    if not new_question:
        await ctx.send("Please write a question!")
        return
    
    # answer guesses in a Nancy hosted game
    if question_game['host'] == bot.user.id:

        # end the game if answer is correct
        if question_game['answer'].lower() in new_question.lower():

            question_dict = {
                "question": new_question,
                "answer": True,
                "author": ctx.message.author.display_name,
                "author_id" : ctx.message.author.id,
                "guess": True
            }
            question_game["questions"].append(question_dict)
            save_question_game(ctx, question_game)

            
            await qstop(ctx, guess=True)
            return
        
        # keep going if incorrect
        else:
            question_dict = {
                "question": new_question,
                "answer": False,
                "author": ctx.message.author.display_name,
                "author_id" : ctx.message.author.id,
                "guess": True
            }
            question_game["questions"].append(question_dict)
            save_question_game(ctx, question_game)

            # end the game if this is the last guess
            if len(questions) > question_game["max_questions"]:
                await qstop(ctx, game_over=True)
                return
    else:
        question_dict = {
            "question": new_question,
            "answer": "",
            "author": ctx.message.author.display_name,
            "author_id" : ctx.message.author.id,
            "guess": True
        }
        question_game["questions"].append(question_dict)
        save_question_game(ctx, question_game)

    embed = create_question_game_embed(question_game, guess=True)
    await ctx.send(embed=embed)

@bot.command(description="View your questions game stats")
async def qstats(ctx):

    # load all stats
    q_dict = load_pkl(ctx, "qstats")

    # if user not seen before add them
    if ctx.message.author.id not in q_dict.keys():
        q_dict[ctx.message.author.id] = create_qstats()
        
        # save new user
        save_pkl(ctx, q_dict, "qstats")

    user_stats = q_dict[ctx.message.author.id]

    embed = discord.Embed(title=f"{ctx.message.author.display_name}'s 20q Stats!")
    embed.add_field(name="Bot Games Played", value=f"{user_stats['bot_participate']}", inline=False)
    embed.add_field(name="Bot Games Won", value=f"{user_stats['bot_win']}", inline=False)
    embed.add_field(name="Bot Game Win Percentage", value=f"{user_stats['bot_win_percent']:.0%}", inline=False)
    embed.add_field(name="Human Games Played", value=f"{user_stats['human_participate']}", inline=False)
    embed.add_field(name="Human Games Won", value=f"{user_stats['human_win']}", inline=False)
    embed.add_field(name="Human Game Win Percentage", value=f"{user_stats['human_win_percent']:.0%}", inline=False)
    embed.add_field(name="Hosted Games", value=f"{user_stats['host_participate']}", inline=False)
    embed.add_field(name="Hosted Games Won", value=f"{user_stats['host_win']}", inline=False)
    embed.add_field(name="Hosted Games Win Percentage", value=f"{user_stats['host_win_percent']:.0%}", inline=False)
    embed.add_field(name="Total Wins", value=f"{user_stats['all_wins']}", inline=False)
    embed.add_field(name="Correct Answers Guessed", value=f"{user_stats['guess_wins']}", inline=False)

    await ctx.send(embed=embed)

@bot.command(description="View your questions game stats")
async def qleader(ctx, stat='all'):
    # load all stats
    q_dict = load_pkl(ctx, "qstats")

    # select the correct leaderboard category
    lname = None
    if stat.lower() == 'all':
        stat = 'all_wins'
        lname = 'All Wins'
    elif stat.lower() == 'human':
        stat = 'human_win'
        lname = 'Human Wins'
    elif stat.lower() == 'bot':
        stat = 'bot_win'
        lname = 'Bot Wins'
    elif stat.lower() == 'host':
        stat = 'host_win'
        lname = 'Host Wins'
    else:
        await ctx.send(f"{stat} is not a valid leaderboard category! (try: all, human, bot or host)")
        return

    # sort by chosen category
    sort_list = [(k, v[stat]) for k, v in sorted(q_dict.items(), key=lambda item: item[1][stat], reverse=True)]
    top_ten = sort_list[:10]

    embed = discord.Embed(title=f"20 Questions {lname} Leaderboard")
    for i, data in enumerate(top_ten):
        user = await bot.fetch_user(data[0])
        embed.add_field(name=f"{i+1}) {user.display_name}", value=f"{data[1]} wins", inline=False)

    await ctx.send(embed=embed)

### ERRORS ###
# Let people know why they can't do things

@like.error
@unlike.error
async def like_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You can only use this command if Nancy likes you")
    else:
        print(error)

@speak.error
@unmod.error
@addmod.error
async def permission_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("You are not authorized to use this command, please contact a mod")
    else:
        print(error)

@crucify.error 
@spankhard.error 
@pats.error
@suss.error 
@tongue.error
@curse.error
@tease.error
@ew.error
@hugs.error
@ravage.error
async def cooldown_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send(f"There is a {DEF_SECONDS} second cooldown on this command, please wait.")
    else:
        print(error)

@qstart.error
async def question_game_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send(f"Please specify a number between {MIN_QUESTIONS} and {MAX_QUESTIONS}")
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"You can only start a game 5 times in 20 minutes, please wait.")
    else:
        print(error)

### UTILS ###
# bunch of small commands to help readability

def write_json(d, loc):
    write_file = json.dumps(d)
    with open(loc, 'w') as out:
        out.write(write_file)

def save_mods(ctx, mod_list):
    with open(f'./mods/{ctx.guild.id}.pkl', 'wb') as f:
        pickle.dump(mod_list, f)
    return mod_list

def load_mods(ctx):
    mod_loc = Path(f'./mods/{ctx.guild.id}.pkl')
    if mod_loc.is_file():
        with open(mod_loc, 'rb') as f:
            mod_list = pickle.load(f)
    else:
        # defaults
        mod_list = [
            CLAIMANT_USER_ID,
            CANCHEZ_USER_ID,
            CARI_USER_ID,
            PHIL_USER_ID,
            POND_USER_ID
        ]
        save_mods(ctx, mod_list)
    return mod_list

def save_likes(ctx, like_list):
    with open(f'./likes/{ctx.guild.id}.pkl', 'wb') as f:
        pickle.dump(like_list, f)
    return like_list

def load_likes(ctx):
    like_loc = Path(f'./likes/{ctx.guild.id}.pkl')
    if like_loc.is_file():
        with open(like_loc, 'rb') as f:
            like_list = pickle.load(f)
    else:
        # defaults
        like_list = [
            CLAIMANT_USER_ID,
            CANCHEZ_USER_ID,
            CARI_USER_ID,
            PHIL_USER_ID,
            POND_USER_ID
        ]
        save_likes(ctx, like_list)
    return like_list

def save_cd(ctx, cd_dict):
    with open(f'./cooldown/{ctx.guild.id}.pkl', 'wb') as f:
        pickle.dump(cd_dict, f)
    return cd_dict

def load_cd(ctx):
    cd_loc = Path(f'./cooldown/{ctx.guild.id}.pkl')
    if cd_loc.is_file():
        with open(cd_loc, 'rb') as f:
            cd_dict = pickle.load(f)
    else:
        # defaults
        cd_dict = {CLAIMANT_USER_ID:{'last_time': datetime.now(tz=pytz.UTC), 'last_cmd': 'cmd'}}
        save_cd(ctx, cd_dict)
    return cd_dict

def save_question_game(ctx, dict):
    loc = f'./questions/{ctx.channel.id}.json'
    write_json(dict, loc)

def load_question_game(ctx):
    question_game_loc = Path(f'./questions/{ctx.channel.id}.json')
    if question_game_loc.is_file():
        with open(f'./questions/{ctx.channel.id}.json', 'r') as inp:
            read_dict = json.load(inp)

        # make keys into ints
        if 'data' in read_dict.keys():
            read_dict['data'] = {int(k):v for k,v in read_dict['data'].items()}
        return read_dict
    else:
        return {}
    
async def send_image_embed(ctx, path, filename, text="", reply=False):
    """
    Send embed with image from path with filename

    Parameters:
    path : string - Path to file (eg. "./images/")
    filename : string - Name of the file (eg. "copium")
    reply : if it should reply to original message
    """
    img = discord.File(f"{path}{filename}", filename=filename)
    embed = discord.Embed()
    embed.set_image(url=f"attachment://{filename}")

    # reply to first message if a reply
    if reply and ctx.message.reference:
        msg = await ctx.fetch_message(ctx.message.reference.message_id)
        await msg.reply(text, file=img, embed=embed)
    else:
        await ctx.send(text, file=img, embed=embed)
    
def create_question_game_embed(game, game_over=False, is_cancelled=False, guess=False):
    """Create embed with question game status"""

    embed = discord.Embed(title="Questions game", description=f"{game['host_name']}'s {game['max_questions']} Questions game")

    nq = len(game["questions"])
    for index, question_dict in enumerate(game["questions"]):
        name = f"{index + 1}. {question_dict['question']} ({question_dict['author']})"
        answer = question_dict["answer"]

        if answer == True:
            answer = "Yes <a:nova_nod_hyper:1269380092740632668>"
        elif answer == False:
            if guess and index+1 == nq and not is_cancelled:
                answer = "<a:who:1270446936457085059> (No)"
            else:
                answer = "No <a:novanope:1251738053639405730>"
        elif answer.lower() in YES_ANSWERS:
            answer = f"{answer} <a:nova_nod_hyper:1269380092740632668>"
        elif answer.lower() in NO_ANSWERS:
            answer = f"{answer} <a:novanope:1251738053639405730>"
        elif answer.lower() == 'unknown':
            answer = "Unknown <:novaidk:1270853670010880021>"

        embed.add_field(name=name, value=answer, inline=False)

    if guess and is_cancelled:
        embed.set_footer(text=f"Game is over! {question_dict['author']} won!")
    elif (len(game["questions"]) == game["max_questions"]) and game['questions'][-1]['answer'] != "":
        embed.set_footer(text="Out of questions, time to guess!")
    elif (len(game["questions"]) > game["max_questions"]) and game['questions'][-1]['answer'] == "":
        embed.set_footer(text="Final Guess!")
    elif game_over:
        embed.set_footer(text="Game is over!")
    elif is_cancelled:
        embed.set_footer(text="Game was cancelled!")
    else:
        max_questions = game["max_questions"]
        current_questions = len(game["questions"])
        questions_left = max_questions - current_questions
        embed.set_footer(text=f"{questions_left} question(s) left")
    
    return embed

def load_20q_characters():
    """Load spreadsheet with 20q questions and characters"""
    i = 0
    data = {}
    header = None
    characters = None
    with open('./20q_characters.csv', 'r') as f:
        
        row_id = None
        for row in f.readlines():
            
            i += 1
            if i == 1:
                header = row.strip().split(',')
                characters = [j for j in header if j not in ['id', 'question', 'unlock_id', 'unlock_answer']]
                continue

            data_dict = {}
            data_row = row.strip().split(',')
            for k in range(len(header)):
                if k == 0:
                    row_id = int(data_row[k])

                if data_row[k] == 'TRUE':
                    data_row[k] = True
                elif data_row[k] == 'FALSE':
                    data_row[k] = False
                elif data_row[k] == '':
                    data_row[k] = None
                elif data_row[k].isnumeric():
                    data_row[k] = int(data_row[k])

                data_dict[header[k]] = data_row[k]
            data[row_id] = data_dict

    return data, characters

def save_pkl(ctx, d, folder):
    with open(f'./{folder}/{ctx.guild.id}.pkl', 'wb') as f:
        pickle.dump(d, f)

def load_pkl(ctx, folder):
    d_loc = Path(f'./{folder}/{ctx.guild.id}.pkl')
    if d_loc.is_file():
        with open(d_loc, 'rb') as f:
            d = pickle.load(f)
    else:
        # empty dict default
        d = {}

        save_pkl(ctx, d, folder)
    return d

def create_qstats():
    # dict of dicts, first key is user_id, then schema below
    d = {
        'bot_participate': 0,
        'bot_win': 0,
        'bot_win_percent': 0.0,
        'host_participate' : 0,
        'host_win' : 0,
        'host_win_percent' : 0.0,
        'human_participate' : 0,
        'human_win' : 0,
        'human_win_percent' : 0.0,
        'all_wins' : 0,
        'guess_wins' : 0
    }

    return d

def calc_qstats(ctx, question_game, guessed):
    
    # load all stats
    q_dict = load_pkl(ctx, "qstats")

    # extract players
    all_players = [q['author_id'] for q in question_game['questions']]
    players = list(set(all_players))
    
    for p_id in players:

        # if user not seen before add them
        if p_id not in q_dict.keys():
            q_dict[p_id] = create_qstats()

        # handle bot games
        if question_game['host'] == bot.user.id:
            
            # calc bot stats
            q_dict[p_id]['bot_participate'] += 1
            if guessed:
                q_dict[p_id]['bot_win'] += 1
                q_dict[p_id]['all_wins'] += 1

                # give credit if they guessed the answer
                if p_id == question_game['questions'][-1]['author_id']:
                    q_dict[p_id]['guess_wins'] += 1

            q_dict[p_id]['bot_win_percent'] = q_dict[p_id]['bot_win'] / q_dict[p_id]['bot_participate']
        
        else:

            # calc player stats
            q_dict[p_id]['human_participate'] += 1
            if guessed:
                q_dict[p_id]['human_win'] += 1
                q_dict[p_id]['all_wins'] += 1

                # give credit if they guessed the answer
                if p_id == question_game['questions'][-1]['author_id']:
                    q_dict[p_id]['guess_wins'] += 1

            q_dict[p_id]['human_win_percent'] = q_dict[p_id]['human_win'] / q_dict[p_id]['human_participate']

    # handle stats for the game host
    if question_game['host'] != bot.user.id:
        
        # find host id
        p_id = question_game['host']
        
        # if user not seen before add them
        if p_id not in q_dict.keys():
            q_dict[p_id] = create_qstats()

        q_dict[p_id]['host_participate'] += 1
        if not guessed:
            q_dict[p_id]['host_win'] += 1
            q_dict[p_id]['all_wins'] += 1
        q_dict[p_id]['host_win_percent'] = q_dict[p_id]['host_win'] / q_dict[p_id]['host_participate']

    # save stat changes
    save_pkl(ctx, q_dict, "qstats")

# private bot key, don't share
with open("./secret", "r") as f:
    secret = f.read()
bot.run(secret)