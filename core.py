### General Imports ###
import os
import pytz
import random
import asyncio
# import subprocess
from datetime import datetime, timedelta

### Discord Imports ###
import discord
from discord.ext import commands

### Local Imports ###
from utils import *
from powermanagement import prevent_standby
from constants import *

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='.', description="Gamemaster bot for Caribdis server", intents=intents)

# remove default help command
bot.remove_command('help')

# stay awake command for self-hosting
# macos
# subprocess.Popen('caffeinate')
# windows
prevent_standby()

@bot.event
async def on_ready():
    # just prints to the console once we login
    print(f'We have logged in as {bot.user}')

    # load Cogs
    await bot.load_extension("hunt")
    await bot.load_extension("aotd")
    await bot.load_extension("qs")
    await bot.load_extension("games")
    await bot.load_extension("misc")

########################
### Always Listening ###
########################

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

    if "shut up nancy" in m:
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

# private bot key, don't share
with open("./secret", "r") as f:
    secret = f.read()
bot.run(secret)