### General Imports ###
import os
import shutil
from pathlib import Path

### Discord Imports ###
import discord
from discord.ext import commands

### Local Imports ###
from utils import can_do
from constants import *

class HOTSWAP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("hotswap loaded")

    @commands.command()
    @commands.check(can_do)
    async def update_cog(self, ctx):
        if len(ctx.message.attachments) != 1:
            await ctx.send("Please provide exactly one file")
            return

        file_name = ctx.message.attachments[0].filename
        if not file_name.endswith('.py'):
            await ctx.send("Please only upload .py files")
            return

        cog_name = file_name.split('.')[0]
        files = [f for f in os.listdir('./cogs') if os.path.isfile(os.path.join('./cogs', f))]
        if file_name not in files:
            await ctx.send("Please only upload files for existing cogs")
            return

        if cog_name == 'hotswap':
            await ctx.send("You cannot hotswap the hotswap cog")

        # remove old file and save new
        cur_loc = f"./cogs/current/{file_name}"
        
        if os.path.isfile(cur_loc):
            os.remove(cur_loc)
        await ctx.message.attachments[0].save(cur_loc)

        # remove old back up and copy new
        active_loc = f"./cogs/{file_name}"
        back_loc = f"./cogs/backup/{file_name}"

        if os.path.isfile(back_loc):
            os.remove(back_loc)
        os.rename(active_loc, back_loc)

        # copy uploaded to active location
        await ctx.message.attachments[0].save(active_loc)

        # load new
        await self.bot.reload_extension(f"cogs.{cog_name}")
        await ctx.send(f"{cog_name} updated and reloaded")

        # catch errors (syntax, extension load error)
        pass

    @commands.command()
    @commands.check(can_do)
    async def rollback_cog(self, ctx, cog_name):
        file_name = cog_name + '.py'
        if file_name not in os.listdir('./cogs'):
            await ctx.send(f"{cog_name} is not a valid cog")
            return

        active_loc = f"./cogs/{file_name}"
        cur_loc = f"./cogs/current/{file_name}"
        back_loc = f"./cogs/backup/{file_name}"

        # check if a backup exists
        if not os.path.isfile(back_loc):
            await ctx.send("No backup present for this cog")
            return

        # delete active cog
        os.remove(active_loc)

        # move backup to active dir
        shutil.copy(back_loc, active_loc)

        # reload previous extension
        await self.bot.reload_extension(f"cogs.{cog_name}")
        await ctx.send(f"{cog_name} rolledback and reloaded")

    @commands.command()
    @commands.check(can_do)
    async def send_cog(self, ctx, cog_name):
        file_name = cog_name + '.py'
        if file_name not in os.listdir('./cogs'):
            await ctx.send(f"{cog_name} is not a valid cog")
            return

        active_loc = f"./cogs/{file_name}"
        active_cog = discord.File(active_loc)
    
        # Send the file
        await ctx.send(file=active_cog, content="Current cog file attached!")

    @commands.command()
    @commands.check(can_do)
    async def add_cog(self, ctx):
        if len(ctx.message.attachments) != 1:
            await ctx.send("Please provide exactly one file")
            return

        file_name = ctx.message.attachments[0].filename
        if not file_name.endswith('.py'):
            await ctx.send("Please only upload .py files")
            return

        cog_name = file_name.split('.')[0]
        files = [f for f in os.listdir('./cogs') if os.path.isfile(os.path.join('./cogs', f))]
        if file_name in files:
            await ctx.send("A cog with that name already exists, please try another name")
            return

        # copy uploaded to active location
        await ctx.message.attachments[0].save(f"./cogs/{file_name}")

        # load new
        await self.bot.load_extension(f"cogs.{cog_name}")
        await ctx.send(f"{cog_name} created and loaded")

    @commands.command()
    @commands.check(can_do)
    async def add_constant(self, ctx, name, value, comment=None):
        with open('./constants.py', 'a') as f:
            f.write('\n\n')

            # add comment above constant if provided
            if comment:
                f.write('#' + comment)
                f.write('\n')

            # add constant
            f.write(f"{name.upper()} = {value}")

        await ctx.send(f"Constant: {name.upper()} = {value} added")

    @update_cog.error
    async def update_error(self, ctx, error):
        if isinstance(error, commands.errors.ExtensionFailed):
            await ctx.send("The extension failed to load, and the update has failed:")
            await ctx.send(f"{error}")
        else:
            await ctx.send(f"{error}")

    @rollback_cog.error
    async def rollback_error(self, ctx, error):
        if isinstance(error, commands.errors.ExtensionFailed):
            await ctx.send("The extension failed to load, and the back up has failed:")
            await ctx.send(f"{error}")
        else:
            await ctx.send(f"{error}")

    @add_cog.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.errors.ExtensionFailed):
            await ctx.send("The extension failed to load, and add has failed:")
            await ctx.send(f"{error}")
        else:
            await ctx.send(f"{error}")

async def setup(bot):
    await bot.add_cog(HOTSWAP(bot))