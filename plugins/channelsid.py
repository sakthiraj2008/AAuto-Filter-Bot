from pyrogram import Client, filters
from info import MOVIE_UPDATE_CHANNEL, ADMINS
from database.users_chats_db import db
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid

MOVIE_UPDATE_CHANNEL = []

@Client.on_message(filters.command("set_channels") & filters.user(ADMINS))
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

@Client.on_message(filters.command("get_channels") & filters.user(ADMINS))
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
        
@Client.on_message(filters.command("set_channel"))
async def set_channel_command(client: Client, message: Message):
    if not ADMINS:
        await message.reply("You do not have permission to use this command.")
        return
    args = message.text.split()
    if len(args) < 8:
        await message.reply("Usage: /set_channel <command_type> <destination_channel_ids> <original:replace> <my_link> <web_link> <my_username> <title>")
        return
    command_type = int(args[1])  # Command type (1, 2, 3, or 4)
    destination_channel_ids = args[2].split(',')  # Destination channel IDs are expected as comma-separated values
    original_text, replace_text = args[3].split(':')  # Text replacement pattern
    my_link = None if args[4] == "None" else args[4]
    web_link = None if args[5] == "None" else args[5]
    my_username = None if args[6] == "None" else args[6]
    title = ' '.join(args[7:])
    data = {
        "command_type": command_type,
        "destination_channel_ids": destination_channel_ids,
        "original_text": original_text,
        "replace_text": replace_text,
        "my_link": my_link,
        "web_link": web_link,
        "my_username": my_username,
        "title": title
    }
    data = await db.set_channel()
    await message.reply(f"Channel settings have been updated for Command Type {command_type} with title '{title}'")

@Client.on_message(filters.command("get_channel"))
async def get_channel_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not ADMINS:
        await message.reply("You do not have permission to use this command.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /get_channel <command_type>")
        return
    command_type = int(args[1])  # Get command_type (1, 2, 3, or 4)
    channel_data = await db.get_channel()
    if channel_data:
        response = f"Command Type {command_type} settings:\n"
        response += f"Destination Channel IDs: {', '.join(channel_data['destination_channel_ids'])}\n"
        response += f"Original Text: {channel_data['original_text']}\n"
        response += f"Replace Text: {channel_data['replace_text']}\n"
        response += f"My Link: {channel_data['my_link'] if channel_data['my_link'] else 'None'}\n"
        response += f"Web Link: {channel_data['web_link'] if channel_data['web_link'] else 'None'}\n"
        response += f"My Username: {channel_data['my_username'] if channel_data['my_username'] else 'None'}\n"
        response += f"Title: {channel_data['title']}\n"
    else:
        response = f"No settings found for Command Type {command_type}."

    await message.reply(response)
