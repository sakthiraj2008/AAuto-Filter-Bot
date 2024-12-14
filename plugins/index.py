import logging, re, asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import LOG_CHANNEL, ADMINS
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp
from pyrogram.types import ForceReply

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()

@Client.on_message((filters.forwarded | (filters.regex("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text) & filters.private & filters.incoming & filters.user(ADMINS))
async def send_for_index(bot, message):
    if message.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match: 
            return await message.reply("❌ Invalid link.")
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int(("-100" + chat_id))
    elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    
    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply("❌ This may be a private channel/group. Make me an admin over there to index the files.")
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("❌ Invalid Link specified.")
    except Exception as e:
        return await message.reply(f"❌ Error: {e}")
    
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply("❌ Make sure I am an admin in the channel if it is private.")
    
    if k.empty:
        return await message.reply("❌ This may be a group, and I am not an admin of the group.")
    
    # Send a confirmation request with ForceReply
    msg = await message.reply(
        f"Do you want to index this channel/group?\n\n"
        f"Chat ID/Username: <code>{chat_id}</code>\n"
        f"Last Message ID: <code>{last_msg_id}</code>\n\n"
        f"Reply with <b>yes</b> or <b>no</b> to confirm.",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=ForceReply(selective=True)  # Enable ForceReply
    )
    
@Client.on_message(filters.reply & filters.text & filters.private)
async def handle_confirmation(bot, reply_message):
    # Check if the reply is tied to the original message
    if reply_message.reply_to_message.message_id == msg.message_id:
        user_response = reply_message.text.strip().lower()  # Trim spaces and convert to lowercase
        
        if user_response in ["yes", "1", "true"]:
            await message.reply("✅ Indexing started!")
            await index_files_to_db(last_msg_id, chat_id, msg, bot)
        elif user_response in ["no", "0", "false"]:
            await message.reply("❌ Indexing canceled.")
        else:
            await message.reply("❌ Invalid response. Please reply with 'yes' or 'no'.")
            
@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    if len(message.command) == 2:
        try: skip = int(message.text.split(" ", 1)[1])
        except: return await message.reply("Skip Number Should Be An Integer.")
        await message.reply(f"Successfully Set Skip Number As {skip}")
        temp.CURRENT = int(skip)
    else:
        await message.reply("Give Me A Skip Number")


async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    async with lock:
        try:
            current = temp.CURRENT
            temp.CANCEL = False
            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                if temp.CANCEL:
                    await msg.edit(f"Successfully Cancelled!!\n\nSaved <code>{total_files}</code> files to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>")
                    break
                current += 1
                if current % 100 == 0:
                    can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
                    reply = InlineKeyboardMarkup(can)
                    try:
                        await msg.edit_text(text=f"Total Messages Fetched: <code>{current}</code>\nTotal Messages Saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>", reply_markup=reply)       
                    except FloodWait as t:
                        await asyncio.sleep(t.value)
                        await msg.edit_text(text=f"Total Messages Fetched: <code>{current}</code>\nTotal Messages Saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>", reply_markup=reply)                          
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                media.file_type = message.media.value
                media.caption = message.caption
                aynav, vnay = await save_file(media)
                if aynav:
                    total_files += 1
                elif vnay == 0:
                    duplicate += 1
                elif vnay == 2:
                    errors += 1       
        except Exception as e:
            logger.exception(e)
            await msg.edit(f'Error: {e}')
        else:
            await msg.edit(f'Succesfully Saved <code>{total_files}</code> To Database!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media Messages Skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>')
            
