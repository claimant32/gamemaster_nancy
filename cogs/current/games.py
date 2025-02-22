### General Imports ###
import re
import pytz
import pickle
import random
import string
import asyncio
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta

### Discord Imports ###
import discord
from discord.ext import commands

### Local Imports ###
from utils import send_image_embed
from vidya_words import vidya_words
from eternum_words import eternum_words
from countries import countries

class GAMES(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("games loaded")

    @commands.command(description="An acro that doesn't suck")
    @commands.max_concurrency(1)
    async def betteracro(self, ctx):
        # acrophonbia from Nadeko, but removing the useless letters (z, q, x)
        # it might make sense to do other smart things like make letters appear
        # in line with their language frequency or similar

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
                m = await self.bot.wait_for('message', check=check1, timeout=5.0)
                
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
                m = await self.bot.wait_for('message', check=check2, timeout=5.0)

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

    @commands.command(description="Two truths and a lie")
    async def truth(self, ctx):
        # Two truths and a lie, classic kids game. One person tells two truths
        # and one lie. Everyone else votes and tries to figure out the lie.

        # Set out the rules
        embed = discord.Embed(title="Two Truths and a Lie")
        embed.add_field(name="Step 1)", value="Player sends me three SEPARATE messages.")
        embed.add_field(name="Step 2)", value="First message is a lie")
        embed.add_field(name="Step 3)", value="Next two messages are true")
        embed.add_field(name="Step 4)", value="Everyone tries to guess the lie!")
        await ctx.send(f'{ctx.message.author.mention} is going to play Two Truths and a Lie!', embed=embed)

        def check1(m):
            # check to make sure we only listen for the person playing the game
            if m.channel.id == ctx.channel.id and m.author.id==ctx.message.author.id:
                return True
            else:
                return False

        # 60 second prompt loop
        lie = None
        truth1 = None
        truth2 = None
        this_time = datetime.now(tz=pytz.UTC)
        await ctx.send(f'{ctx.message.author.mention} send your lie:')
        while (datetime.now(tz=pytz.UTC) - this_time).total_seconds() < 60:
            
            try:
                # save their lie and truths one at a time
                m = await self.bot.wait_for('message', check=check1, timeout=60.0)
                if not lie:
                    lie = m.content
                    await m.delete()
                    await ctx.send('Now your first truth:')
                elif not truth1:
                    truth1 = m.content
                    await m.delete()
                    await ctx.send('And your second truth:')
                elif not truth2:
                    truth2 = m.content
                    await m.delete()
                    break
            except asyncio.TimeoutError:
                continue
            else:
                continue

        if not truth2:
            await ctx.send("You didn't provide two truths and a lie!")
            return
        else:
            # mix up the options and ask people to vote
            mixed = [lie, truth1, truth2]
            random.shuffle(mixed)
            embed = discord.Embed(title="Two Truths and a Lie! You have 30 seconds to vote for the LIE with a number!")
            embed.add_field(name = f"Number 1:", value = mixed[0])
            embed.add_field(name = f"Number 2:", value = mixed[1])
            embed.add_field(name = f"Number 3:", value = mixed[2])
            await ctx.send(embed=embed)

        def check2(m):
            # listen only for votes on the right channel and 1-3
            if m.channel.id == ctx.channel.id:
                if not m.content.isdigit():
                    return False
                elif int(m.content) in [1,2,3]:
                    return True
                else:
                    return False
            else:
                return False

        # 60 second vote loop
        votes = {}
        this_time = datetime.now(tz=pytz.UTC)
        while (datetime.now(tz=pytz.UTC) - this_time).total_seconds() < 30:
            
            try:
                m = await self.bot.wait_for('message', check=check2, timeout=5.0)
                
                # skip empty messages that timeout
                if m == None:
                    continue

                # prevent double votes
                if m.author.name in votes.keys():
                    continue
                
                # prevent liar from voting
                if m.author.name == ctx.author.name:
                    continue

                # capture votes and delete them
                votes[m.author.name] = m.content
                await m.delete()
                await ctx.send(f"{m.author.display_name} has voted!")
            except asyncio.TimeoutError:
                continue
            else:
                continue

        # make sure someone votes
        if len(votes) == 0:
            await ctx.send("No one voted, now you will never know what is true and what is a lie!")
            return
        else:
            # find the most common vote and how many times it was voted
            win_num, count = Counter(votes.values()).most_common(1)[0]

            # determine if everyone figure it out or not and send to the channel
            if mixed[int(win_num)-1] == lie:
                embed = discord.Embed(title="You all guessed right!")
            else:
                embed = discord.Embed(title="You all guessed wrong! Better luck next time!")
            embed.add_field(name = f"Guessed Lie: {mixed[int(win_num)-1]} with {count} votes", 
                            value = f"Actual Lie: {lie}")
            await ctx.send(embed=embed)

    @commands.command(description="Hangman with more categories")
    @commands.max_concurrency(1)
    async def alleyman(self, ctx, category=None):
        # Like Nadeko's hangman, but with new categories
        
        # block DM playing
        if isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.send("Can't play in DMs, sorry!")
            return

        filename = "body.png"

        if not category:
            await ctx.send("Please pick a category you would like to use! (currently eternum, videogames or countries)")
            return

        if 'videogames' == category:
            word = random.choice(vidya_words)
        elif 'eternum' == category:
            word = random.choice(eternum_words)
        elif 'countries' == category:
            word = random.choice(countries)
        else:
            await ctx.send(f"{category} is not a valid alleyman category")
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
                m = await self.bot.wait_for('message', check=check, timeout=5.0)
                
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

async def setup(bot):
    await bot.add_cog(GAMES(bot))