from pyrogram import Client, filters
from info import MOVIE_UPDATE_CHANNEL, ADMINS
from database.users_chats_db import db

MOVIE_UPDATE_CHANNEL = []

@Client.on_message(filters.command("set_channel") & filters.user(ADMINS))
async def set_channel(bot, message):
    global MOVIE_UPDATE_CHANNEL
    try:
        command_args = message.text.split(" ", 1)
        if len(command_args) != 2:
            await message.reply_text("Usage: `set_channel <channel_id1> <channel_id2> ...`")
            return
        channel_ids = command_args[1].split()
        new_channels = []
        for channel_id in channel_ids:
            if channel_id.startswith("-") and channel_id[1:].isdigit():
                new_channels.append(int(channel_id))
            else:
                await message.reply_text(f"Invalid channel ID: `{channel_id}`")
                return
        MOVIE_UPDATE_CHANNEL = new_channels
        await db.set_movie_update_channels(MOVIE_UPDATE_CHANNEL)
        await message.reply_text(
            f"Successfully updated the channels: `{', '.join(map(str, MOVIE_UPDATE_CHANNEL))}`"
        )
    except Exception as e:
        print(f"Error in set_channel: {e}")
        await message.reply_text(f"An error occurred: `{e}`")

@Client.on_message(filters.command("get_channel") & filters.user(ADMINS))
async def get_channel(bot, message):
    try:
        channels = await db.get_movie_update_channels()
        if not channels:
            channels = MOVIE_UPDATE_CHANNEL
        channels_list = "\n".join([str(channel) for channel in channels])
        await message.reply_text(f"Current movie update channels:\n\n{channels_list}")
    except Exception as e:
        print(f"Error in get_channel: {e}")
        await message.reply_text(f"An error occurred: `{e}`")
        
