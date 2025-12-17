### Local Imports ###
import os
import math
import time
import random
import pickle
from pathlib import Path

### Discord Imports ###
import discord
from discord import app_commands
from discord.ext import commands

### Local Imports ###
from constants import *
from utils import can_do, spam_channel

eter = ['alex', 'annie', 'dalia', 'luna', 'nancy', 'nova', 'penny']
secret = ['calypso', 'eva', 'maat']
eter_gold = ['alex', 'annie', 'dalia', 'luna', 'nancy', 'nova', 'penny', 'calypso']
oialt = ['judie', 'lauren', 'jasmine', 'iris', 'aiko', 'carla', 'rebecca']

teams_ids = {
    921059611031781416 : 'penny',
    921060154496155650 : 'nova',
    919557542026297385 : 'nancy',
    919371718924054529 : 'dalia',
    921060038678822972 : 'luna',
    921060110204289076 : 'alex',
    921059129039155270 : 'annie'
}

ass_role = {
    CNC_GUILD : 1300135081238724750,
    CARI_GUILD : 1320740212250513421
}

class AOTD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("aotd loaded")
    
    @commands.hybrid_command(description="Collect your Ass of the Day")
    @commands.check(spam_channel)
    @commands.cooldown(1, 72000, commands.BucketType.user)
    async def aotd(self, ctx):

        # set the image
        img = discord.File('./aotd/ass_of_the_day.gif', filename="aotd.gif")
        embed = discord.Embed(title=f"Spin the Wheel! Be blessed!")
        embed.set_image(url="attachment://aotd.gif")

        await ctx.send(embed=embed, file=img, view=Spinner(ctx))

    @commands.check(spam_channel)
    @commands.hybrid_command(description="Check on your AOTD progress", aliases=["aotd_collections", "acollection", "acollections", "asscollection"])
    @app_commands.describe(
        guild_id="[Admin only] Force Discord guild",
        user_id="[Admin only] Force Discord user"
    )
    async def aotd_collection(self, ctx, guild_id: int | None=None, user_id: int | None=None):
        # Handle Guild, ignore if anybody else
        if guild_id and ctx.message.author.id in [CLAIMANT_USER_ID, CANCHEZ_USER_ID]:
            guild = int(guild_id)
        else:
            guild = ctx.guild.id
        aotd_dict = load_aotd(guild)

        # Handle User, ignore if anybody else
        if user_id and ctx.message.author.id in [CLAIMANT_USER_ID, CANCHEZ_USER_ID]:
            user = int(user_id)
            # Get User's display name, use ID as fallback
            user_data = self.bot.get_user(user)
            if user_data:
                username = user_data.display_name
            else:
                username = user
            # Get Guild's display name, use ID as fallback
            guild_data = self.bot.get_guild(guild)
            if guild_data:
                guild_name = guild_data.name
            else:
                guild_name = guild

            m = f"Here is the status of ass collection of {username} from {guild_name}!"
            empty_m = f"{username} haven't collected any asses yet in {guild_name}!"
        else:
            user = ctx.message.author.id
            m = "Here is the status of your ass collection!"
            empty_m = "You haven't collected any asses yet! Try .aotd first!"

        if user not in aotd_dict.keys():
            await ctx.send(empty_m)
            return

        coll = aotd_dict[user]

        embed = discord.Embed()
        for girl, status in coll['eter'].items():
            embed.add_field(name=girl.capitalize(), value="✅ Collected!" if status else "❌ Missing!")

        if any(coll['secret'].values()):
            for girl, status in coll['secret'].items():
                embed.add_field(name=girl.capitalize(), value="✅ Collected!" if status else "❌ Missing!")

        if any(coll['oialt'].values()):
            for girl, status in coll['oialt'].items():
                embed.add_field(name=girl.capitalize(), value="✅ Collected!" if status else "❌ Missing!")

        if any(coll['eter_gold'].values()):
            for girl, status in coll['eter_gold'].items():
                embed.add_field(name="Gold" + girl.capitalize(), value="✅ Collected!" if status else "❌ Missing!")

        await ctx.send(m, embed=embed)
    
    @commands.command()
    @commands.check(can_do)
    async def add_aotd_role(self, ctx):
        if len(ctx.message.mentions) == 0:
            await ctx.send('Who do you want grant the role to?')
        elif len(ctx.message.mentions) == 1:
            await add_ass_role(ctx, ctx.message.mentions[0].id)
        else:
            await ctx.send('I can only add one role at a time')

    @commands.command()
    @commands.check(can_do)
    async def remove_aotd_role(self, ctx):
        if len(ctx.message.mentions) == 0:
            await ctx.send('Who do you want remove the role from?')
        elif len(ctx.message.mentions) == 1:
            await remove_ass_role(ctx, ctx.message.mentions[0].id)
        else:
            await ctx.send('I can only remove one role at a time')

    @commands.command()
    @commands.check(can_do)
    async def grant_ass(self, ctx, user, girl, gold=False):
        if len(ctx.message.mentions) == 0:
            await ctx.send('What user are you granting the ass to?')
        
        elif len(ctx.message.mentions) == 1:
            
            # load claimed asses
            a_id = ctx.message.mentions[0].id
            aotd_dict = load_aotd(CARI_GUILD)
            if a_id not in aotd_dict.keys():
                aotd_dict[a_id] = {}
                aotd_dict[a_id]['eter'] = {g:False for g in eter}
                aotd_dict[a_id]['secret'] = {g:False for g in secret}
                aotd_dict[a_id]['eter_gold'] = {g:False for g in eter_gold}
                aotd_dict[a_id]['oialt'] = {g:False for g in oialt}
                aotd_dict[a_id]['last_two'] = [None, None]

            # save results
            if gold and girl.lower() in eter:
                aotd_dict[a_id]['eter_gold'][girl.lower()] = True
            elif girl.lower() in eter:
                aotd_dict[a_id]['eter'][girl.lower()] = True
            elif girl.lower() in secret:
                aotd_dict[a_id]['secret'][girl.lower()] = True
            elif girl.lower() in oialt:
                aotd_dict[a_id]['oialt'][girl.lower()] = True
            else:
                await ctx.send("Not a valid ass to grant")
                return

            # don't include granted asses in history
            # aotd_dict[a_id]['last_two'] = [girl.lower(), l2[0]]
            save_aotd(CARI_GUILD, aotd_dict)
            await ctx.send(f"Girl: {girl}, Gold: {gold} ass granted")
        
        else:
            await ctx.send('Only one ass grant at a time')

    @commands.command()
    @commands.check(can_do)
    async def gib_harem(self, ctx):
        await grant_harem(ctx, bot=self.bot)
        return

    @aotd.error
    async def cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            aotd_dict = load_aotd(ctx.guild.id)
            coll = aotd_dict[ctx.message.author.id]
            last_ass = coll['last_two'][0]

            if last_ass in eter:
                loc = f'./aotd/eter/{last_ass}.png'
            elif last_ass in secret:
                loc = f'./aotd/secret/{last_ass}.png'
            elif last_ass in oialt:
                loc = f'./aotd/oialt/{last_ass}.png'
            elif last_ass in eter_gold:
                loc = f'./aotd/gold/{last_ass}.png'

             # set the image
            img = discord.File(loc, filename="scene.png")
            embed = discord.Embed(title=f"Your ass of the day is {last_ass.capitalize()}! Lucky you!")
            embed.set_image(url="attachment://scene.png")

            next_time = int(time.time() + error.retry_after)
            await ctx.send(f"You've already claimed your ass today! Try again <t:{next_time}:R>", embed=embed, file=img)
        else:
            aotd.reset_cooldown(ctx)
            await ctx.send("An unexpected error occured, I have reset your cooldown, try again!")
            print(error)

    async def cog_command_error(self, ctx, error):
        print(error)

async def setup(bot):
    await bot.add_cog(AOTD(bot))

def save_aotd(guild_id, aotd_dict):
    with open(f'./aotd/{guild_id}.pkl', 'wb') as f:
        pickle.dump(aotd_dict, f)
    return aotd_dict

def load_aotd(guild_id):
    aotd_loc = Path(f'./aotd/{guild_id}.pkl')
    if aotd_loc.is_file():
        with open(aotd_loc, 'rb') as f:
            aotd_dict = pickle.load(f)
    else:
        # defaults
        aotd_dict = {}
        save_aotd(guild_id, aotd_dict)
    return aotd_dict

async def grant_harem(ctx, bot):
    # get cari guild
    guild = bot.get_guild(CARI_GUILD)
    # get self
    member = await guild.fetch_member(1269059788139135038)
    # get harem role
    new_role = guild.get_role(924021576645627924)

    # skip if already added
    if new_role in member.roles:
        ctx.send("User already has the role!")
        return

    # add role
    await member.add_roles(new_role)

    # send message to channel
    await ctx.send("Successfully added harem role")

async def add_ass_role(ctx, user_id):
    # get role and user
    guild = ctx.guild
    member = await guild.fetch_member(user_id)
    new_role = guild.get_role(ass_role[guild.id])

    # skip if already added
    if new_role in member.roles:
        ctx.send("User already has the role!")
        return

    # add role
    await member.add_roles(new_role)

    # send message to channel
    await ctx.send("Butt Collector Role Added!")

async def remove_ass_role(ctx, user_id):
    # get role and user
    guild = ctx.guild
    member = await guild.fetch_member(user_id)
    new_role = guild.get_role(ass_role[guild.id])

    # skip if not already added
    if new_role not in member.roles:
        ctx.send("User doesn't have the role!")
        return

    # add role
    await member.remove_roles(new_role)

    # send message to channel
    await ctx.send("Ass Collector Role Removed!")

class Spinner(discord.ui.View):

    def __init__(self, ctx):
        self.ctx = ctx
        super().__init__()

    @discord.ui.button(label="Claim Dat Ass!", style=discord.ButtonStyle.green)
    async def claim(self, interaction, button):
        await interaction.response.defer()

        # load claimed asses
        a_id = self.ctx.message.author.id
        aotd_dict = load_aotd(interaction.guild_id)
        if a_id not in aotd_dict.keys():
            aotd_dict[a_id] = {}
            aotd_dict[a_id]['eter'] = {g:False for g in eter}
            aotd_dict[a_id]['secret'] = {g:False for g in secret}
            aotd_dict[a_id]['eter_gold'] = {g:False for g in eter_gold}
            aotd_dict[a_id]['oialt'] = {g:False for g in oialt}
            aotd_dict[a_id]['last_two'] = [None, None]

        ### add keys for asses added later ###

        # gold Calypso
        if 'calypso' not in aotd_dict[a_id]['eter_gold'].keys():
            aotd_dict[a_id]['eter_gold']['calypso'] = False

        sg = False
        new = False
        gold = False
        cursed = False
        li_done = all(aotd_dict[a_id]['eter'].values())
        sg_done = all(aotd_dict[a_id]['secret'].values())
        oialt_done = all(aotd_dict[a_id]['oialt'].values())
        l2 = aotd_dict[a_id]['last_two']

        odds = random.random()
        if li_done and sg_done:
            # pool of all asses (5% SG, 75% eter, 20% oialt)
            if odds <= .0001:
                cursed = True
                loc = './aotd/cursed'
            elif odds <= .05: # or self.pwd=="sidegirl":
                sg = True
                loc = './aotd/secret'
            elif odds <= .20: # or self.pwd=="oialt":
                loc = './aotd/oialt'
            else:
                loc = './aotd/eter'
        else:
            # 1/20 chance to get sg
            if odds <= .0001:
                cursed = True
                loc = './aotd/cursed'
            elif odds <= .05: # or self.pwd=="sidegirl":
                sg = True
                loc = './aotd/secret'
            else:
                loc = './aotd/eter'

        # get teams roles
        teams = []
        for r in self.ctx.author.roles:
            if r.id in teams_ids.keys():
                teams += [teams_ids[r.id]]

        # Make 3rd in a row a guarantee for team roles
        if (l2[0] == l2[1]) and l2[0] in teams and not aotd_dict[a_id]['eter_gold'][l2[0]]:

            bypass = True
            girl = l2[0].capitalize()

        else:
            bypass = False

            # pick a random png
            p = Path(loc)
            ops = list(p.glob('*.png'))
            s = random.choice(ops)
            girl = s.name.split('.')[0].capitalize()

        # handle golden
        if (girl.lower() in eter_gold and girl.lower() == l2[0] and girl.lower() == l2[1]) or bypass:
            gold = True
            s = f'./aotd/gold/{girl.lower()}.png'        

        # save results
        if gold:
            if aotd_dict[a_id]['eter_gold'][girl.lower()]:
                new = False
            else:
                new = True
                aotd_dict[a_id]['eter_gold'][girl.lower()] = True
        elif girl.lower() in eter:
            if aotd_dict[a_id]['eter'][girl.lower()]:
                new = False
            else:
                new = True
                aotd_dict[a_id]['eter'][girl.lower()] = True
        elif girl.lower() in secret:
            if aotd_dict[a_id]['secret'][girl.lower()]:
                new = False
            else:
                new = True
                aotd_dict[a_id]['secret'][girl.lower()] = True
        elif girl.lower() in oialt:
            if aotd_dict[a_id]['oialt'][girl.lower()]:
                new = False
            else:
                new = True
                aotd_dict[a_id]['oialt'][girl.lower()] = True
        
        if not cursed:
            aotd_dict[a_id]['last_two'] = [girl.lower(), l2[0]]
            save_aotd(interaction.guild_id, aotd_dict)

        # disable the button
        button.disabled = True
        button.label = f"{girl}!"

        # set the image
        img = discord.File(s, filename="scene.png")
        if new:
            embed = discord.Embed(title=f"Your ass of the day is {girl}! Lucky you! (New Ass)")
        else:
            embed = discord.Embed(title=f"Your ass of the day is {girl}! Lucky you! (Already Collected)")
        embed.set_image(url="attachment://scene.png")

        m = ""
        # check for first time set completions
        if all(aotd_dict[a_id]['eter'].values()) and not li_done:
            if sg_done:
                m += "You have collected all Eternum LI and SG asses! Congrats! \n"
                m += "You have unlocked a small chance to encounter OiaLT asses now, try and collect them all!\n"
            else:
                m += "You have collected all Eternum LI asses! Congrats!\n"
                m += "Collect all the Side Girl asses to unlock more secrets!"
        elif all(aotd_dict[a_id]['secret'].values()) and not sg_done:
            if li_done:
                m += "You have collected all Eternum LI and SG asses! Congrats! \n"
                m += "You have unlocked a small chance to encounter OiaLT asses now, try and collect them all!\n"
            else:
                m += "You have collected all Eternum SG asses! Congrats!\n"
                m += "Collect all the Main Girl asses to unlock more secrets!\n"
        elif all(aotd_dict[a_id]['oialt'].values()) and not oialt_done:
            m += "You have collected all OiaLT LI asses! Congrats!\n"
            m += "You have completed the main part of the game, congrats on winning the Butt Collector role!\n"
            m += "Try and collect the Golden Asses (get 3 in a row of the Eternum LIs) if you want to overachieve!\n"
            await add_ass_role(self.ctx, a_id)

        # check if they have found rare outcomes
        if gold:
            m += "You have found a mythical golden ass! You are rewarded for getting the same girl 3 times in a row!"
        elif sg:
            m += "You have found a rare secret Side Girl ass!"
        elif cursed:
            m += "The Ghost of WendO has visited you and cursed you with a glimpse of the fattest ass in Eternum... Orion Richards"

        await interaction.edit_original_response(content=m, embed=embed, attachments=[img], view=self)