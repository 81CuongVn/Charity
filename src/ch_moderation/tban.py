import discord
from discord.ext import commands
from ch_boot.startup import *
from ch_boot.cmongodb import *
from ch_discord_utils.issue_penalty import ch_ban
import datetime, time, typing

@charity.command()
@commands.has_any_role("Alpha tester", 840545860101210122, 830486598050119740, 843198710782361682, 836122037009121312)
async def tban(ctx, member: discord.User, duration: float, del_msg_history: typing.Optional[int] = 0, *, message_arg):
    if ctx.author.top_role.position <= member.top_role.position:
        raise Exception("Cannot execute moderation commands for members ranked same or higher than you.")
    await ch_ban(
        issuer = ctx.author,
        server_id = ctx.guild.id,
        member_id = member.id,
        duration = duration,
        delete_message_days = del_msg_history,
        reason = message_arg
    )
    tse = time.time()
    retrieved = clc_usrinfract.find_one({ "guild_id" : ctx.guild.id, "user_id" : member.id})
    if retrieved != None:
        clc_usrinfract.update_one(
            {
                "guild_id" : ctx.guild.id,
                "user_id" : member.id
            },
            {
                "$push" : {
                    "active_timed_infractions" : {
                        "penalty" : "tban",
                        "ini_tse" : tse,
                        "infraction" : message_arg,
                        "termination_tse" : duration * 24 * 60 + tse
                    }
                }
            }
        )
        clc_usrinfract.update_one(
            {
                "guild_id" : ctx.guild.id,
                "user_id" : member.id
            },
            {
                "$push" : {
                    "infractions_record" : f'[{datetime.datetime.utcfromtimestamp(tse).isoformat()}] `Temporary ban for {duration} day(s):` {message_arg}'
                }
            }
        )
    else:
        infract_obj = {
            "guild_id" : ctx.guild.id,
            "user_id" : member.id,
            "active_timed_infractions" : [],
            "infractions_record" : [
                f'[{datetime.datetime.utcfromtimestamp(tse).isoformat()}] `Temporary ban for {duration} day(s):` {message_arg}'
            ]
        }
        clc_usrinfract.insert_one(infract_obj)
    await ctx.message.add_reaction("☑️")

@tban.error
async def tban_error(ctx, error):
    msg = error
    await ctx.reply(msg)