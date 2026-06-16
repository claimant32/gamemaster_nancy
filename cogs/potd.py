### General Imports ###
import os
import math
import time
import json
import random
import pickle
from pathlib import Path

### Discord Imports ###
import discord
from discord.ext import commands

### Local Imports ###
from utils import *

class POTD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("potd loaded")
    
    @commands.command()
    @commands.check(spam_channel)
    @commands.cooldown(1, 72000, commands.BucketType.user)
    async def potd(self, ctx, pwd=None):

        # set the image
        img = discord.File('./potd/penny_emotion_spin.gif', filename="potd.gif")
        embed = discord.Embed(title=f"What's Your Emotion Today? Click to Find Out!")
        embed.set_image(url="attachment://potd.gif")

        await ctx.send(embed=embed, file=img, view=Spinner(ctx, pwd))

    @potd.error
    async def cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            next_time = int(time.time() + error.retry_after)
            await ctx.send(f"You've already discovered your emotion today! Try again <t:{next_time}:R>")
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            self.potd.reset_cooldown(ctx)
            await ctx.send("An unexpected error occured, I have reset your cooldown, try again!")
            print(error)
    
    async def cog_command_error(self, ctx, error):
        print(error)

async def setup(bot):
    await bot.add_cog(POTD(bot))

def pick_an_emo(loc):
    # pick a random png
    p = Path(loc)
    ops = list(p.glob('*.png'))
    s = random.choice(ops)
    emo = s.name.split('.')[0]

    return s, emo

class Spinner(discord.ui.View):

    def __init__(self, ctx, pwd):
        self.ctx = ctx
        self.pwd = pwd
        super().__init__()

    @discord.ui.button(label="Get Your Emotion!", style=discord.ButtonStyle.green)
    async def claim(self, interaction, button):
        await interaction.response.defer()
        s, emo = pick_an_emo('./potd/')

        # disable the button
        button.disabled = True
        button.label = f"{emo}!"

        # get a random fortune cookie
        with open('./emotions.json', 'r') as f:
            em = json.load(f)

        # handle both angers
        if emo.startswith("Anger"):
            horoscope = random.choice(em['Anger'])
        else:
            horoscope = random.choice(em[emo])

        m = f"Chop-Chop's Fortune Cookie Says: '{horoscope}'"

        # set the image
        img = discord.File(s, filename="scene.png")
        embed = discord.Embed(title=f"Your emotion for today is {emo}!", description=m)
        embed.set_image(url="attachment://scene.png")

        await interaction.edit_original_response(embed=embed, attachments=[img], view=self)