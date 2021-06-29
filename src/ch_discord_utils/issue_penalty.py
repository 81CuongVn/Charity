import discord
from ch_boot.startup import *
from ch_boot.cmongodb import *
from ch_discord_utils.embed_generator import *
import typing

async def ch_ban(issuer: typing.Union[discord.Member, discord.User], server_id, member_id, reason = None, duration = None, delete_message_days = 0):
    guild = charity.get_guild(server_id)
    user = charity.get_user(member_id)
    await user.send(embed = meta_message(description = "**`{}:`** You have been *banned*.\n**`INFRACTION:`** {}".format(guild.name, reason)))
    await guild.ban(
        user = user,
        reason = reason,
        delete_message_days = delete_message_days
    )
    gconfig = clc_gconfig.find_one({"_id" : server_id})
    if gconfig["moderation_config"]["logger_config"]["module_active"]:
        if gconfig["moderation_config"]["logger_config"]["bool_on_member_ban"]:
            dump = charity.get_channel(gconfig["moderation_config"]["logger_config"]["logger_log_dump_text_channel_id"])
            if duration == None:
                await dump.send(
                    embed = create_embed(
                        author_name = issuer,
                        author_icon_url = issuer.avatar_url,
                        title = "**:hammer: Ban**",
                        description = f"**Banned** {user} _(ID: `{user.id}`)_\n**Reason:** {reason}\n",
                        colour = 0x67aa30
                    )
                )
            else:
                await dump.send(
                    embed = create_embed(
                        author_name = issuer,
                        author_icon_url = issuer.avatar_url,
                        title = "**:hammer: Temporary Ban**",
                        description = f"**Banned** {user} _(ID: `{user.id}`)_ for {duration} day(s)\n**Reason:** {reason}\n",
                        colour = 0x67aa30
                    )
                )

async def ch_unban(issuer: typing.Union[discord.Member, discord.User], server_id, member_id, reason = None):
    guild = charity.get_guild(server_id)
    user = charity.get_user(member_id)
    await guild.unban(
        user = user,
        reason = reason,
    )
    await user.send(embed = meta_message(description = "**`{}:`** You have been *unbanned*.\n**`REASON`** {}".format(guild.name, reason)))
    gconfig = clc_gconfig.find_one({"_id" : server_id})
    if gconfig["moderation_config"]["logger_config"]["module_active"]:
        if gconfig["moderation_config"]["logger_config"]["bool_on_member_unban"]:
            dump = charity.get_channel(gconfig["moderation_config"]["logger_config"]["logger_log_dump_text_channel_id"])
            await dump.send(
                embed = create_embed(
                    title = "**:cake: Unban**",
                    description = f"**Unbanned** {user} _(ID: `{user.id}`)_\n**Reason:** {reason}\n",
                    colour = 0x67aa30,
                    author_name = issuer,
                    author_icon_url = issuer.avatar_url
                )
            )

async def ch_warn(issuer: typing.Union[discord.Member, discord.User], server_id, member_id, reason = None):
    guild = charity.get_guild(server_id)
    user = charity.get_user(member_id)
    await user.send(embed = meta_message(description = "**`{}:`** You have been *warned*.\n**`INFRACTION:`** {}".format(guild.name, reason)))
    gconfig = clc_gconfig.find_one({"_id" : server_id})
    if gconfig["moderation_config"]["logger_config"]["module_active"]:
        if gconfig["moderation_config"]["logger_config"]["bool_nonapi_warn"]:
            dump = charity.get_channel(gconfig["moderation_config"]["logger_config"]["logger_log_dump_text_channel_id"])
            await dump.send(
                embed = create_embed(
                    title = "**:warning: Warning**",
                    description = f"**Warned** {user} _(ID: `{user.id}`)_\n**Reason:** {reason}\n",
                    colour = 0xff6700,
                    author_name = issuer,
                    author_icon_url = issuer.avatar_url
                )
            )

async def ch_mute(issuer: typing.Union[discord.Member, discord.User], server_id, member_id, reason = None, duration = None):
    guild = charity.get_guild(server_id)
    member = guild.get_member(member_id)
    gconfig = clc_gconfig.find_one({"_id" : server_id})
    muted_role = guild.get_role(gconfig["moderation_config"]["mute_config"]["guild_mute_role_id"])
    if muted_role == None: raise Exception("Mute role hasn't been setup for this server.")
    await member.add_roles(muted_role)
    await member.send(embed = meta_message(description = f"**`{guild.name}:`** You have been muted for *{duration} minute(s)*" + ("" if reason == None else f"\n**INFRACTION:** {reason}")))

async def ch_unmute(issuer: typing.Union[discord.Member, discord.User], server_id, member_id, reason = None):
    guild = charity.get_guild(server_id)
    member = guild.get_member(member_id)
    gconfig = clc_gconfig.find_one({"_id" : server_id})
    muted_role = guild.get_role(gconfig["moderation_config"]["mute_config"]["bool_guild_mute_role_id"])
    if muted_role == None: raise Exception("Mute role hasn't been setup for this server.")
    await member.remove_roles(muted_role)
    await member.send(embed = meta_message(description = f"**`{guild.name}:`** You have been unmuted." + ("" if reason == None else f"\n**REASON:** {reason}")))

async def ch_kick(issuer: typing.Union[discord.Member, discord.User], server_id, member_id, reason = None):
    guild = charity.get_guild(server_id)
    member = guild.get_member(member_id)
    await member.send(embed = meta_message(description = f"**`{guild.name}:`** You have been kicked." + ("" if reason == None else f"\n**REASON:** {reason}")))
    await guild.kick(member, reason = reason)