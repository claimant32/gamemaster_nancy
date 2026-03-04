### General Imports ###
import json
import random
from pathlib import Path

### Discord Imports ###
import discord
from discord import app_commands
from discord.ext import commands

### Local Imports ###
from constants import *
from utils import spam_channel
from utils import write_json, load_pkl, save_pkl, can_do, send_image_embed

#################
### Constants ###
#################

# QUESTION_GAME_PATH = "./question_game.json"

DEFAULT_QUESTIONS = 15 # Default amount of questions
MIN_QUESTIONS = 1 # Min amount of questions
MAX_QUESTIONS = 25 # Max amount of questions

NO_ANSWERS = ["n", "no", "nope"] # Answers that will add NO emoji
YES_ANSWERS = ["y", "yes", "yep", "yeah"] # Answers that will add YES emoji

class QS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("20qs loaded")

    @commands.hybrid_command(description="Rules for the question game")
    async def qrules(self, ctx):
        embed = discord.Embed(title="Questions Game Rules")
        embed.add_field(name="1)", value="The character you pick must either be named or have a line in the game", inline=False)
        embed.add_field(name="2)", value="You can't ask questions about version numbers", inline=False)
        embed.add_field(name="3)", value="A Love Interest is one of the 7 main girls in the gallery screen (side girls do not count, including Calypso).", inline=False)
        embed.add_field(name="4)", value="An NPC is a character in Eternum that is not controlled by an Earth human (but they can still be people. Ex: Praetorian's are NPCs, so is Roach the horse in the Wild West Server).", inline=False)
        embed.add_field(name="5)", value="When playing in bot mode, the bot will answer certain questions as false unless it is explicitly stated in the game as true. Ex: We don't know if Professor Bundledore has kids, but he doesn't mention them so the bot will answer no", inline=False)
        embed.add_field(name="6)", value="When playing in bot mode and guessing, default to guessing the player's first name if we know it and their last name otherwise", inline=False)
        embed.add_field(name="7)", value="Some characters don't have names but are fun to guess. In these cases, guess what the game calls them in their dialoge (Ex: 'Granny' from the phone call in 0.1)", inline=False)
        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Start Questions game")
    @commands.check(spam_channel)
    @commands.cooldown(10, 1200, type=commands.BucketType.user)
    @app_commands.describe(
        max_questions="How many questions to play",
        host="Who should ask the questions?",
    )
    @app_commands.choices(host=[
        app_commands.Choice(name="Myself", value="human"),
        app_commands.Choice(name="The bot", value="bot"),
    ])
    async def qstart(self, ctx, max_questions: int = DEFAULT_QUESTIONS, host: str = 'human'):
        """Start Questions game if not started already by creating and saving json"""

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
                "host": self.bot.user.id,
                "host_name": self.bot.user.display_name,
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
            await self.q_nancy(ctx, question_game, question_game['questions'])

    @commands.hybrid_command(description="Stop 20 question game")
    @app_commands.describe(
        game_over="Whether the person lost",
        guess="Whether the person won",
    )
    async def qstop(self, ctx, game_over: bool = False, guess: bool = False):
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

        if ctx.message.author.id in (question_game["host"], first_asker) or await can_do(ctx) or game_over or guess:

            # handle Nancy/Bot games
            answer = None
            nancy_game = False
            if question_game['host'] == self.bot.user.id:
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

                # send image embed if a bot game
                await ctx.send("You guessed correctly. Nice!")
                if nancy_game:
                    await send_image_embed(ctx, './q_characters/', f"{answer.lower()}.jpg", text=f"The correct answer was: {answer}")

            elif game_over:

                # process stats for this game
                calc_qstats(ctx, q_game, guessed=False)

                await ctx.send("Your guess was wrong, game over!")

                # share the answer if it's a Nancy hosted game
                if nancy_game:
                    await send_image_embed(ctx, './q_characters/', f"{answer.lower()}.jpg", text=f"The correct answer was: {answer}")
            
            else:    
                await ctx.send("The Questions game is stopped!")
            
        else:
            await ctx.send("Only host or mods can stop the game!")

    @commands.hybrid_command(description="Submit a question")
    @app_commands.describe(q_option="Number of the question to ask")
    async def q(self, ctx, q_option: int | None = None):
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
        if question_game['host'] == self.bot.user.id:
            
            # make sure they sent a question selection
            if not q_option:
                await ctx.send("Please select a question option!")
                return

            # make sure question not asked already
            if q_option in question_game['asked']:
                await ctx.send(f"Question #{q_option} has already been asked!")
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
        if question_game['host'] == self.bot.user.id:
            # don't add question options if last question
            if not len(questions) == question_game["max_questions"]:
                await self.q_nancy(ctx, question_game, questions)
            else:
                embed = create_question_game_embed(question_game)
                await ctx.send(embed=embed)
        else:
            embed = create_question_game_embed(question_game)
            await ctx.send(embed=embed)

    async def q_nancy(self, ctx, question_game, questions, shuffle=False):
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

    @commands.hybrid_command(description="List all bot questions")
    async def qlist(self, ctx):
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

    @commands.hybrid_command(description="Shuffle questions available to be asked")
    async def qshuffle(self, ctx):
        question_game = load_question_game(ctx)

        if not question_game:
            return

        await self.q_nancy(ctx, question_game, question_game['questions'], True)

    @commands.hybrid_command(description="Answer a question")
    async def qa(self, ctx):
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
            await self.qstop(ctx, guess=True)
            return
        
        last_question["answer"] = answer
        question_game["questions"][-1] = last_question

        save_question_game(ctx, question_game)

        # end game if you are above amount of questions and allow guess as final
        if len(questions) > question_game["max_questions"]:
            await self.qstop(ctx, game_over=True)
        else:
            embed = create_question_game_embed(question_game)

            await ctx.send(embed=embed)

    @commands.hybrid_command(description="Show current state of Question game")
    async def qs(self, ctx):
        """ Show current game status """
        question_game = load_question_game(ctx)
        embed = create_question_game_embed(question_game)

        if question_game['host'] == self.bot.user.id:
            await self.q_nancy(ctx, question_game, question_game['questions'])
            return

        await ctx.send(embed=embed)

    @commands.hybrid_command(description="Discard last question")
    async def qdiscard(self, ctx):
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

    @commands.hybrid_command(description="Guess the character")
    async def guess(self, ctx):
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
        if question_game['host'] == self.bot.user.id:

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
                
                await self.qstop(ctx, guess=True)
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
                    await self.qstop(ctx, game_over=True)
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

    @commands.hybrid_command(description="View your questions game stats")
    @commands.check(spam_channel)
    async def qstats(self, ctx):

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

    @commands.hybrid_command(description="View your questions game stats")
    @commands.check(spam_channel)
    async def qleader(self, ctx, stat='all'):
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
            user = await self.bot.fetch_user(data[0])
            embed.add_field(name=f"{i+1}) {user.display_name}", value=f"{data[1]} wins", inline=False)

        await ctx.send(embed=embed)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"Please specify a number between {MIN_QUESTIONS} and {MAX_QUESTIONS}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown, try again in {round(error.retry_after)}s")
        else:
            print(error)

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
    
def create_question_game_embed(game, game_over=False, is_cancelled=False, guess=False):
    """Create embed with question game status"""

    embed = discord.Embed(title="Questions game", description=f"{game['host_name']}'s {game['max_questions']} Questions game")

    nq = len(game["questions"])
    for index, question_dict in enumerate(game["questions"]):
        name = f"{index + 1}. {question_dict['question']} ({question_dict['author']})"
        answer = question_dict["answer"]

        if answer == True:
            answer = "Yes <a:8_NovaNodHyper:972495321139671100>"
        elif answer == False:
            if guess and index+1 == nq and not is_cancelled:
                answer = "<a:who:1373854639975563316> (No)"
            else:
                answer = "No <a:NovaNoppers:1251738053639405730>"
        elif answer.lower() in YES_ANSWERS:
            answer = f"{answer} <a:8_NovaNodHyper:972495321139671100>"
        elif answer.lower() in NO_ANSWERS:
            answer = f"{answer} <a:NovaNoppers:1251738053639405730>"
        elif answer.lower() == 'unknown':
            answer = "Unknown <:NovaShrug:1270853670010880021>"

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
        if question_game['host'] == NANCY_USER_ID:
            
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
    if question_game['host'] != NANCY_USER_ID:
        
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

async def setup(bot):
    await bot.add_cog(QS(bot))