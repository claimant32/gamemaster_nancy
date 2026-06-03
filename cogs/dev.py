### Discord Imports ###
import discord
from discord.ext import commands

### Local Imports ###
from constants import *

roles = [
    1082389296411050024, # Member
    926796229311102996, # Founder
    790862472256028705, # Demon Lord
    1212922490267901962, # Demon Lord (S)
    753230720109117501, # God
    948610288708648972, # God (S)
    707615662805090497, # Eternumite
    1157584763356446740, # Eternumite (S)
    707615960336433298, # Master
    1212922502246957066, # Master (S)
    707616036169711698, # Supporter
    1212922505115996261, # Supporter (S)
    707616195687219220, # Follower
    1212925040912236584, # Follower (S)
]

class DEV(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("dev loaded")

    @commands.command(description="Fetch pledgers count")
    async def getpledgers(self, ctx):
        if ctx.author.id not in [CLAIMANT_USER_ID, CANCHEZ_USER_ID]:
            return
        guild = self.bot.get_guild(CARI_GUILD)
        embed = discord.Embed(title="Pledgers:")
        for role_id in roles:
            role = guild.get_role(role_id)
            embed.add_field(name=role.name, value=len(role.members))

        await ctx.send(embed=embed)

    ### Errors ### 
    # Let people know why they can't do things

    @getpledgers.error
    async def getpledgers_error(self, ctx, error):
        await ctx.send(error)

async def setup(bot):
    await bot.add_cog(DEV(bot))