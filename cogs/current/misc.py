### General Imports ###
import re
import os
import random
import typing
import asyncio
from pathlib import Path

### Discord Imports ###
import discord
from discord.ext import commands

### Local Imports ###
from utils import *

class MISC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("misc loaded")

    @commands.command(description='List command categories')
    async def cmd(self, ctx, cmdtype=None):

        if not cmdtype:
            # list each category of commands
            embed = discord.Embed()
            embed.add_field(name=".cmd", value="List all categories of commands, you are using it now!")
            embed.add_field(name=".cmdmod", value="All mod only commands")
            embed.add_field(name=".cmdinteract", value="All commands for interacting with other people")
            embed.add_field(name=".cmdgames", value="All commands for games you can play")
            embed.add_field(name=".cmdquestion", value="Commands for the 20 questions game")
            embed.add_field(name=".cmdaotd", value="Ass of the Day Commands!")
            embed.add_field(name=".cmdmisc", value="Everything else (mostly memes)")
            embed.set_footer(text="You can also use .cmd <subcommand> like '.cmd games'")

            await ctx.send("Here are all the different categories of commands!", embed=embed)
        
        elif cmdtype == 'mod':
            await self.cmdmod(ctx)
            return
        elif cmdtype == 'interact':
            await self.cmdinteract(ctx)
            return
        elif cmdtype == 'games':
            await self.cmdgames(ctx)
            return
        elif cmdtype == 'question':
            await self.cmdquestion(ctx)
            return
        elif cmdtype == 'misc':
            await self.cmdmisc(ctx)
            return
        elif cmdtype == 'aotd':
            await self.cmdaotd(ctx)
            return
        else:
            await ctx.send(f"'{cmdtype}' is not a valid subcommand")

    @commands.command(description='List all mod commands')
    async def cmdmod(self, ctx):
        embed = discord.Embed()
        embed.add_field(name=".addmod", value="Add a new Nancy moderator")
        embed.add_field(name=".unmod", value="Remove a Nancy moderator")
        embed.add_field(name=".speak", value="Speak in a channel as Nancy")

        await ctx.send("Here are all the moderator commands", embed=embed)

    @commands.command(description='List all interaction commands')
    async def cmdinteract(self, ctx):
        embed = discord.Embed()
        embed.add_field(name = ".mods", value = "Mods are here")
        embed.add_field(name = ".pizzatime", value = "Pizza for Jaque")
        embed.add_field(name = ".greet", value = "Send a custom gif greeting to a user")
        embed.add_field(name = ".addgreet", value = "Add a new greeting gif for a user")
        embed.add_field(name = ".crucify", value = "Crucify your enemies, long live the WRE")
        embed.add_field(name = ".spank", value = "Find out who can take it harder than Penny")
        embed.add_field(name = ".spankhard", value = "Really show 'em how it's done")
        embed.add_field(name = ".pats", value = "Who has been good lately? Reward them")
        embed.add_field(name = ".like", value = "Ask Nancy to like someone, can only be done by people she already likes")
        embed.add_field(name = ".unlike", value = "Ask Nancy to not like someone, can only be done by people she already likes")
        embed.add_field(name = ".bday", value = "Wish a friend Happy Birthday!")
        embed.add_field(name = ".rizz", value = "Try to rizz up a friend, see what happens if you are succesful")
        embed.add_field(name = ".rizzstats", value = "If you have found all the secret endings you can check your stats!")
        embed.add_field(name = ".tongue", value = "Random render from Eternum with a tongue involved")
        embed.add_field(name = ".suss", value = "Call out suspicious behavior")
        embed.add_field(name = ".hugs", value = "Hug your friends!")
        embed.add_field(name = ".kisses", value = "Kiss your friends!")
        embed.add_field(name = ".curse", value = "Curse evil comments")
        embed.add_field(name = ".ew", value = "Express disgust")
        embed.add_field(name = ".surprise", value = "A surprise for you from Rod")
        embed.add_field(name = ".yes", value = "Agree with someone")
        embed.add_field(name = ".no", value = "Disagree with someone (cutely)")
        embed.add_field(name = ".begone", value = "Keep the thots off you")
        embed.add_field(name = ".confused", value = "When people are talking nonsense")
        embed.add_field(name = ".wtf", value = "When people be wildin' out")

        await ctx.send("Here are all the interaction commands", embed=embed)

    @commands.command(description='List all game commands')
    async def cmdgames(self, ctx):
        embed = discord.Embed()
        embed.add_field(name = ".betteracro", value = "Play acro, but without dumb letters")
        embed.add_field(name = ".truth", value = "Play two truths and a lie!")
        embed.add_field(name = ".alleyman", value = "Play hangman with more categories!")
        embed.add_field(name = ".loadup", value = "Reload with bullets and shields")
        embed.add_field(name = ".inv", value = "View your inventory and stats")
        embed.add_field(name = ".leader", value = "Display the loadup Top 10")
        embed.add_field(name = ".shoot", value = "Use your bullets to shoot people!")
        embed.add_field(name = ".bet", value = "Bet bullets for a chance to win more!")

        await ctx.send("Here are all the game commands", embed=embed)

    @commands.command(description="List Question game commands")
    async def cmdquestion(self, ctx):
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

    @commands.command(description='List all aotd commands')
    async def cmdaotd(self, ctx):
        embed = discord.Embed()
        embed.add_field(name = ".aotd", value = "Ass of the Day roulette!")
        embed.add_field(name = ".aotd_collection", value = "See which asses you have collected (and find secrets!)")
       
        await ctx.send("Here are all the Ass of the Day commands", embed=embed)

    @commands.command(description='List all misc commands')
    async def cmdmisc(self, ctx):
        embed = discord.Embed()
        embed.add_field(name = ".fillerup", value = "Fulfill Luna's hunger")
        embed.add_field(name = ".hypnotits", value = "Fall into a titty trance")
        embed.add_field(name = ".hypnoass", value = "Fall into a ass trance")
        embed.add_field(name = ".gm", value = "Say good morning!")
        embed.add_field(name = ".gn", value = "Say good night!")
        embed.add_field(name = ".typing", value = "When someone is pulling a ball™ typing")
        embed.add_field(name = ".reacted", value = "When someone is pulling a ball™ reacting")
        embed.add_field(name = ".yoink", value = "Yoink an emoji or a sticker")
        await ctx.send("Here are all the misc. commands", embed=embed)

    ####################
    ### Mod Commands ###
    ####################

    @commands.command(description="Add a mod")
    @commands.check(can_do)
    async def addmod(self, ctx):
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

    @commands.command(description="Remove a mod")
    @commands.check(can_do)
    async def unmod(self, ctx):
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

    @commands.command(description="Have Nancy talk")
    @commands.check(can_do)
    async def speak(self, ctx):

        if len(ctx.message.channel_mentions) == 1:
            await ctx.message.delete()
            channel = ctx.message.channel_mentions[0]
            msg = '>'.join(ctx.message.content.split('>')[1:])
            await channel.send(msg)
        else:
            await ctx.send("Please specify a channel")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, id=1331686531253145712)
        await member.add_roles(role)

    #######################
    ### People Commands ###
    #######################

    @commands.command(description='Mods are here')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def mods(self, ctx):
        await send_image_embed(ctx, "./images/", "ans.png")

    @commands.command(description='Fair custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def fair(self, ctx):
        await send_image_embed(ctx, "./images/", "fair.gif")

    @commands.command(description='Pizza for Jaque')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def pizzatime(self, ctx):
        await send_image_embed(ctx, "./images/", "pizzatime.gif")

    @commands.command(description='Mods are here')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def heity(self, ctx):
        await send_image_embed(ctx, "./images/", "heity.png")

    @commands.command(description='Sara custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def sara(self, ctx):
        await send_image_embed(ctx, "./images/", "sara.png")

    @commands.command(description='Wimpie custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def wimpie(self, ctx):
        await send_image_embed(ctx, "./images/", "wimpie.jpg")

    @commands.command(description='Wingy custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def wingy(self, ctx):
        await send_image_embed(ctx, "./images/", "wingy.png")

    @commands.command(description='Peanut custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def peanut(self, ctx):
        await send_image_embed(ctx, "./images/", "peanut.gif")

    @commands.command(description='Greet people with custom reacts')
    @commands.check(general_channel)
    async def greet(self, ctx):
        # extract user_id
        if len(ctx.message.mentions) == 0:
            await ctx.send('Who do you want me to greet? Tag them in this command')
        elif len(ctx.message.mentions) == 1:
            await send_image_embed(ctx, "./greetings/", f'{ctx.message.mentions[0].id}.gif')
        else:
            await ctx.send('I can only greet one person at a time!')

    @commands.command(description="Add new .greet gifs react")
    async def addgreet(self, ctx):
        #Add new image file to .greet command
        attachments = ctx.message.attachments

        # Check for exactly 1 attachment
        if len(attachments) != 1:
            await ctx.send("Please attach 1 file!")
        else:
            attachment = attachments[0]
            content_type = attachment.content_type
            if "image" not in content_type:
                await ctx.send("Please attach an image/gif!")
            elif len(ctx.message.mentions) == 0:
                await ctx.send("Please tag the person you want add a greeting for!")
            elif len(ctx.message.mentions) > 1:
                await ctx.send("Please only tag one person to add a greeting at a time")
            else:
                await attachment.save(fp=f"./greetings/{ctx.message.mentions[0].id}.gif")
                await ctx.send(f"New greeting for {ctx.message.mentions[0].display_name} added!")

    @commands.command(description='Ball custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def dropkick(self, ctx):
        # this one is a bit special in that it only works on Ball

        if len(ctx.message.mentions) == 0:
            await ctx.send('Who do you want to kick? Tag them in this command')
        elif len(ctx.message.mentions) == 1:
            if ctx.message.mentions[0].id == BALL_USER_ID:
                await send_image_embed(ctx, "./images/", "ball.gif", text=f"{ctx.message.author.mention} kicked {ctx.message.mentions[0].mention} to the moon!")
            else:
                await send_image_embed(ctx, "./images/", "no_effect.jpg", text="It had no effect! Try something else!")
        else:
            await ctx.send('Only kick one person at a time!')

    @commands.command(description='Canchez custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def canchez(self, ctx):
        c_user = await self.bot.fetch_user(CANCHEZ_USER_ID)
        await send_image_embed(ctx, "./images/", "canchez.gif", text=f"{c_user.mention}, fetch me my render! (and remember to pat the retriever in payment!)")

    @commands.command(description="Load a new extension")
    @commands.check(can_do)
    async def load(self, ctx, ext):
        await self.bot.load_extension(f"cogs.{ext}")
        await ctx.send(f"{ext} loaded")

    @commands.command(description="Reload an extension")
    @commands.check(can_do)
    async def reload(self, ctx, ext):
        await self.bot.reload_extension(f"cogs.{ext}")
        await ctx.send(f"{ext} reloaded")
        
    ############################
    ### Interaction Commands ###
    ############################

    @commands.command(description='Attempt to ravage bathrobe Nancy as she deserves')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.check(spam_channel)
    async def ravage(self, ctx):

        # deny ravage attempts (unless they are lucky)
        n = random.randint(1,20)

         # punch if not liked
        if await nancy_likes_you(ctx):

            # 20% chance to actually ravage
            if n >= 17 or ctx.author.id == REZZ_USER_ID:

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

    @commands.command(description='For uncooperative server users')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def crucify(self, ctx):
        # meme from Eternum, @someone to crucify them like the leader of the ERE

        # need to mention exactly one person
        if len(ctx.message.mentions) == 0:
            await ctx.send('Who should we crucify today?')
        elif len(ctx.message.mentions) == 1:
            await send_image_embed(ctx, "./images/", "crucify.png", text=f"Maximo, crucify {ctx.message.mentions[0].display_name}!")
        else:
            await ctx.send('I can only crucify one person at a time')

    @commands.command(description='For extremely uncooperative server users')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.check(spam_channel)
    async def spank(self, ctx):

        if len(ctx.message.mentions) == 0:
            await ctx.send('Who deserves a spanking?')
        
        elif len(ctx.message.mentions) == 1:

            # catch people trying to spank Nancy
            if ctx.message.mentions[0] == self.bot.user:
                await send_image_embed(ctx, "./images/", "naughty.gif", text=f"{ctx.message.author.display_name} you've been naughty for trying to spank Mommy, time out for you!")
                return

            n = random.randint(1,20)
            if n == 1:
                await send_image_embed(ctx, "./images/", "spear.png", text="Their partner saw you approaching and speared you in the fucking eye!")
                
            else:
                n = random.choice([1,3])
                await send_image_embed(ctx, "./images/", f"spank{n}.gif", text=f"{ctx.message.author.display_name} spanked {ctx.message.mentions[0].display_name}!")
        else:
            await ctx.send('I can only spank one person at a time')

    @commands.command(description='For extremely uncooperative server users part 2')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.check(spam_channel)
    async def spankhard(self, ctx):

        if len(ctx.message.mentions) == 0:
            await ctx.send('Who deserves a spanking?')

        elif len(ctx.message.mentions) == 1:

            # catch people trying to spank Nancy
            if ctx.message.mentions[0] == self.bot.user:
                await send_image_embed(ctx, "./images/", "naughty.gif", text=f"{ctx.message.author.mention} you've been naughty for trying to spank Mommy, time out for you!")
                return

            n = random.randint(1,20)
            if n == 1:
                await send_image_embed(ctx, "./images/", "alley.png", text="Shouldn't have taken that shortcut...")
            else:
                n = random.choice([2,4])
                await send_image_embed(ctx, "./images/", f"spank{n}.gif", text=f"{ctx.message.author.display_name} spanked {ctx.message.mentions[0].display_name} even harder (and they liked it)!")
        else:
            await ctx.send('I can only spank one person at a time')

    @commands.command(description='Just pats between friends')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def pats(self, ctx):
        # meme from Eternum, @someone to pat them like Nova!

        # only pat exactly one person
        if len(ctx.message.mentions) == 0:
            await ctx.send('Who do you want to pat? Tag them with this command.')
        elif len(ctx.message.mentions) == 1:
            # unique react for patting Nancy
            if ctx.message.mentions[0] == self.bot.user:

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
            await send_image_embed(ctx, "./images/", f"pats{n}.gif", text=f"{ctx.message.author.display_name} pat {ctx.message.mentions[0].display_name} on the head!")
        else:
            await ctx.send('One at a time for pats please!')

    @commands.command(description="Put someone on Nancy's good side")
    @commands.check(nancy_likes_you)
    async def like(self, ctx):
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

    @commands.command(description="Put someone on Nancy's bad side")
    @commands.check(nancy_likes_you)
    async def unlike(self, ctx):
        like_list = load_likes(ctx)
        if '.unlike' not in ctx.message.content:
            like_list.remove(ctx.message.author.id)
            await ctx.send(f"{ctx.message.author.display_name} you are a creep, leave me alone!")
            save_likes(ctx, like_list)
        elif len(ctx.message.mentions) == 0:
            await ctx.send("Who should I not like?")
        elif len(ctx.message.mentions) == 1:
            if ctx.message.mentions[0].id == REZZ_USER_ID:
                await ctx.send("I cannot unlike Rezz, he is my sworn sword and shield")
            elif ctx.message.mentions[0].id in like_list:
                like_list.remove(ctx.message.mentions[0].id)
                await ctx.send(f"{ctx.message.mentions[0].display_name} is a creep, leave me alone!")
                save_likes(ctx, like_list)
            else:
                await ctx.send(f"Can't unlike someone I don't already like silly")

        else:
            await ctx.send('I can only unlike one person at a time')

    @commands.command(description='Wish your friends Happy Birthday')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def bday(self, ctx, user, girl=None):
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

    @commands.command(description='Random tongue render')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def tongue(self, ctx):

        # pick a random png
        p = Path('./tongue')
        ops = list(p.glob('*.png'))
        s = random.choice(ops)

        # set the image
        img = discord.File(s, filename="scene.png")
        embed = discord.Embed()
        embed.set_image(url="attachment://scene.png")

        await ctx.send(f"Nyahh", file=img, embed=embed)

    @commands.command(description='Random hug render')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def hugs(self, ctx):

        # pick a random png
        p = Path('./hugs')

        if ctx.author.id == WINGY_USER_ID:
            ops = list(p.glob('*penny*'))
        elif ctx.author.id == PEANUT_USER_ID:
            ops = list(p.glob('*alex*'))
        else:
            ops = list(p.glob('*.png'))
        s = random.choice(ops)

        # set the image
        img = discord.File(s, filename="scene.png")
        embed = discord.Embed()
        embed.set_image(url="attachment://scene.png")

        await ctx.send(f"Come here!", file=img, embed=embed)

    @commands.command(description='Random kiss render')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def kisses(self, ctx):

        # pick a random png
        p = Path('./kisses')

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

    #####################
    ### Misc Commands ###
    #####################

    @commands.command(description='Fillerup custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.check(spam_channel)
    async def fillerup(self, ctx):
                
        # pick a random gif
        p = Path('./fill')
        ops = list(p.glob('*.png'))
        s = random.choice(ops)

        # select random number
        n = random.randint(1, 20)

        if n == 1 or 'opensesame' in ctx.message.content:
            await send_image_embed(ctx, "./images/", "grope.png")
        else:
            img = discord.File(s, filename="fill.png")
            embed = discord.Embed()
            embed.set_image(url="attachment://fill.png")
            await ctx.send(file=img, embed=embed)

    @commands.command(description='Yes custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def yes(self, ctx):
        
        # delete and respond to og message if a reply
        reply = False
        await ctx.message.delete()
        if ctx.message.reference:
            reply = True

        await send_image_embed(ctx, "./images/", "yes.gif", "", reply)

    @commands.command(description='No custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def no(self, ctx):
        
        # delete and respond to og message if a reply
        reply = False
        await ctx.message.delete()
        if ctx.message.reference:
            reply = True

        await send_image_embed(ctx, "./images/", "no.gif", "", reply)

    @commands.command(description='WTF custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def wtf(self, ctx):
        
        # delete and respond to og message if a reply
        reply = False
        await ctx.message.delete()
        if ctx.message.reference:
            reply = True

        await send_image_embed(ctx, "./images/", "tray_wtf.png", "", reply)

    @commands.command(description='Begone custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def begone(self, ctx):
        
        # delete and respond to og message if a reply
        reply = False
        if ctx.message.reference:
            await ctx.message.delete()
            reply = True

        await send_image_embed(ctx, "./images/", "begone.png", text="BEGONE THOT!", reply=True)

    @commands.command(description='Confused custom react')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def confused(self, ctx):

        # delete and respond to og message if a reply
        reply = False
        if ctx.message.reference:
            await ctx.message.delete()
            reply = True

        await send_image_embed(ctx, "./images/", "confused.gif", text="You are making me dizzy...", reply=True)

    @commands.command(description='Goodmorning custom react')
    async def gm(self, ctx):
        p = Path('./images')
        ops = list(p.glob('gm*'))
        s = random.choice(ops)
        await send_image_embed(ctx, "./images/", s.__str__().split("\\")[-1])

    @commands.command(description='Goodnight custom react')
    async def gn(self, ctx):
        p = Path('./images')
        ops = list(p.glob('gn*'))
        s = random.choice(ops)
        await send_image_embed(ctx, "./images/", s.__str__().split("\\")[-1])

    @commands.command(description='Use for suspect behavior')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def suss(self, ctx):
        n = random.randint(1,6)

        await send_image_embed(ctx, "./images/", f"suss{n}.gif")

    @commands.command(description='Use for hypnotits')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def hypnotits(self, ctx):
        await send_image_embed(ctx, "./images/", "hypno.gif")

    @commands.command(description='Use for hypnoass')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def hypnoass(self, ctx):
        await send_image_embed(ctx, "./images/", "hypno_ass.gif")

    @commands.command(description="When someone pulling a ball™ typing", aliases=["typing", "type", "balltype"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def balltyping(self, ctx):
        await send_image_embed(ctx, "./images/", "balltyping.png")

    @commands.command(description="When someone pulling a ball™ reacting", aliases=["reacted", "react", "ballreact"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ballreacted(self, ctx):
        await send_image_embed(ctx, "./images/", "ballreacted.png")

    @commands.command(description='Curse evil comments')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def curse(self, ctx):

        # delete and respond to og message if a reply
        reply = False
        if ctx.message.reference:
            await ctx.message.delete()
            reply = True

        await send_image_embed(ctx, "./images/", "curse.png", "", reply)

    @commands.command(description='Call out brutish behavior')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def uncivil(self, ctx):

        # delete and respond to og message if a reply
        reply = False
        if ctx.message.reference:
            await ctx.message.delete()
            reply = True

        await send_image_embed(ctx, "./images/", "uncivilized.png", "Loutish. Mannerless. UNCIVILIZED", reply)

    @commands.command(description='Express disgust')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ew(self, ctx):

        # delete and respond to og message if a reply
        reply = False
        if ctx.message.reference:
            await ctx.message.delete()
            reply = True

        await send_image_embed(ctx, "./images/", "ew.gif", "", reply)

    @commands.command(description='Screw you, from Rod')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def surprise(self, ctx):

        # delete and respond to og message if a reply
        reply = False
        if ctx.message.reference:
            await ctx.message.delete()
            reply = True

        await send_image_embed(ctx, "./images/", "rod_finger.gif", "", reply)

    @commands.command(description="Yoink an emoji to the server or get URL of a sticker")
    async def yoink(self, ctx, index: typing.Optional[int]=None, method: typing.Literal["url", "add"] = "url"):
        # Yoink an emoji or a sticker to a server

        reference = ctx.message.reference
        if not reference:
            await ctx.send("Reply to a message with an emoji or a sticker you want to yoink!")
            return

        message = reference.resolved
        if not message or type(message) is discord.DeletedReferencedMessage:
            print("Error resolving reference message to yoink!")
            return
        
        stickers = message.stickers
        # If message has stickers, send URL of the first one (technically the only one)
        if stickers:
            sticker_item = stickers[0]
            sticker = await sticker_item.fetch()
            await ctx.send(sticker.url)
            return

        content = message.content
        if not content:
            return
        
        # Find all emojis in the message
        emojis = re.findall(EMOJI_REGEX, content)

        if not emojis:
            await ctx.send("No emoji found!")
            return
        elif not index:
            if len(emojis) > 1:
                await ctx.send("Multiple emoji found, specify which one you want to yoink with index `.yoink N`")
                return
            else:
                index = 1
        elif index and index > len(emojis) or index == 0:
            await ctx.send(f"Incorrect index!")
            return
        
        emoji_str = emojis[index - 1]
        # Create partial emoji from <a:name:id> string
        partial_emoji = discord.PartialEmoji.from_str(emoji_str)
        # Add connection to allow .read()
        partial_emoji = discord.PartialEmoji.with_state(self.bot._connection, name=partial_emoji.name, animated=partial_emoji.animated, id=partial_emoji.id)

        # Check if emoji is already on the server (dumdum protection)
        if partial_emoji.id in [e.id for e in ctx.guild.emojis]:
            await ctx.send(f"Emoji is already on this server!")
            guild_emoji = ctx.guild.get_emoji(partial_emoji.id)
            await ctx.send(f"{guild_emoji}")
            return
        
        # Revert to "url" if not a mod
        if method == "add" and not await can_do(ctx):
            await ctx.send("Only mods can add emoji! Sending a link instead")
            await ctx.send(partial_emoji.url)
            return
        
        if method == "url":
            await ctx.send(partial_emoji.url)
        else:
            await ctx.send("Downloading...")
            emoji_bytes = await partial_emoji.read()
            created_emoji = await ctx.guild.create_custom_emoji(name=partial_emoji.name, image=emoji_bytes, reason=f"Yoinked by {ctx.author.display_name}")

            await ctx.send(f"Yoinked an emoji {created_emoji.name}")
            await ctx.send(f"{created_emoji}")

    @commands.command(description="Check if Nancy is alive")
    async def heartbeat(self, ctx):
        await ctx.send("I am here!")
        
    ##############
    ### Errors ###
    ##############
    @like.error
    @unlike.error
    async def like_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("You can only use this command if Nancy likes you")
        else:
            print(error)

    @speak.error
    @addmod.error
    @unmod.error
    async def permission_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("You are not authorized to use this command, please contact a mod")
        else:
            print(error)

    @yoink.error
    async def yoink_errors(self, ctx, error):
        if isinstance(error, discord.NotFound):
            await ctx.send("Emoji was deleted!")
        elif isinstance(error, discord.Forbidden) or isinstance(error, commands.CommandInvokeError):
            await ctx.send("Bot lacks permissions to add emoji!")
        elif isinstance(error, discord.HTTPException):
            await ctx.send("HTTP Exception occured!")
        elif isinstance(error, discord.DiscordException):
            await ctx.send("Can't download emoji asset!")
            # print in case other errors are subclasses
            print(error)
        else:
            print(error)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown, try again in {round(error.retry_after)}s")
        else:
            print(error)

async def setup(bot):
    await bot.add_cog(MISC(bot))