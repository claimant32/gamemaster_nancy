import json
import pickle
import discord
from pathlib import Path

### Local imports ###
from constants import *

##############
### Checks ###
##############

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

    # server boosters automatically liked
    if CARI_BOOSTER_ROLE in [r.id for r in ctx.author.roles]:
        return True
    elif ctx.author.id in users or await can_do(ctx):
        return True
    else:
        return False

async def spam_channel(ctx):
    # check if in the spam channel
    if ctx.channel.id not in [BOT_AND_SPAM, TEST_CHANNEL]:
        await ctx.send(f"You can only do that in <#{BOT_AND_SPAM}>")
        return False
    else:
        return True

#######################
### Disk operations ###
#######################

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

def write_json(d, loc):
    write_file = json.dumps(d)
    with open(loc, 'w') as out:
        out.write(write_file)

##############
### Embeds ###
##############

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

##############################
### Specific pickle checks ###
##############################
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
            REZZ_USER_ID,
            CLAIMANT_USER_ID,
            CANCHEZ_USER_ID
        ]
        save_likes(ctx, like_list)
    return like_list