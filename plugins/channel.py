from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import INDEX_CHANNELS, LOG_CHANNEL, MOVIE_UPDATE_CHANNEL
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import get_poster, temp
import re
from database.users_chats_db import db

processed_movies = set()
media_filter = filters.document | filters.video

@Client.on_message(filters.chat(INDEX_CHANNELS) & media_filter)
async def media(bot, message):
    bot_id = bot.me.id
    media = getattr(message, message.media.value, None)
    if media.mime_type in ['video/mp4', 'video/x-matroska']: 
        media.file_type = message.media.value
        media.caption = message.caption
        success_sts = await save_file(media)
        if success_sts == 'suc' and await db.get_send_movie_update_status(bot_id):
            file_id, file_ref = unpack_new_file_id(media.file_id)
            await send_movie_updates(bot, file_name=media.file_name, caption=media.caption, file_id=file_id)

async def get_imdb(file_name):
    imdb_file_name = await movie_name_format(file_name)
    imdb = await get_poster(imdb_file_name)
    if imdb and 'poster' in imdb:
        return imdb.get('poster')
    return "https://telegra.ph/file/88d845b4f8a024a71465d.jpg"  # Default poster

async def movie_name_format(file_name):
    # Clean and format the movie name
    filename = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name)
                      .replace('_', ' ').replace('[', '').replace(']', '')
                      .replace('(', '').replace(')', '').replace('{', '')
                      .replace('}', '').replace('.', ' ').replace('@', '')
                      .replace(':', '').replace(';', '').replace("'", '')
                      .replace('-', '').replace('!', '')).strip()
    return filename

async def check_qualities(text, qualities):
    quality = [q for q in qualities if q.lower() in text.lower()]
    return ", ".join(quality)

async def check_languages(text, languages):
    matched_languages = []
    for lang, abbreviations in languages.items():
        for abbr in abbreviations:
            if abbr.lower() in text.lower():
                matched_languages.append(lang)
                break  # Avoid duplicate detection
    return " + ".join(matched_languages)

async def send_movie_updates(bot, file_name, caption, file_id):
    try:
        channels = await db.get_movie_update_channels() or MOVIE_UPDATE_CHANNEL

        # Extract year and season
        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else "Not Available"
        season_match = re.search(r"(?i)(?:s|season)0*(\d{1,2})", caption)
        season = season_match.group(1) if season_match else None

        # Set movie quality
        qualities = ["HDCAM", "HDRip", "SDTV", "HDTV", "BluRay", "HD DVD", "WEB-DL", "CAMRip", "PreDVD", 
                     "DVDscr", "WEB-HD", "BDRip", "DVDRip", "HDTS"]
        quality = await check_qualities(caption, qualities) or "HDRip"

        # Detect languages
        language_map = {
            "Tamil": ["Tamil", "Tam"],
            "Bengali": ["Bengali", "Ben"],
            "English": ["English", "Eng"],
            "Marathi": ["Marathi", "Mar"],
            "Hindi": ["Hindi", "Hin"],
            "Telugu": ["Telugu", "Tel"],
            "Malayalam": ["Malayalam", "Mal"],
            "Kannada": ["Kannada", "Kan"],
            "Punjabi": ["Punjabi", "Pun"],
            "Gujarati": ["Gujarati", "Guj"],
            "Korean": ["Korean", "Kor"],
            "Japanese": ["Japanese", "Jap"],
            "Bhojpuri": ["Bhojpuri", "Bjp"],
            "Chinese": ["Chinese", "Ch"],
            "Dual": ["Dual"],
            "Multi": ["Multi"]
        }
        language = await check_languages(caption, language_map) or "Not Available"

        # Format movie name
        movie_name = await movie_name_format(file_name)
        if movie_name in processed_movies:
            return
        processed_movies.add(movie_name)

        # Remove year from movie name
        if year != "Not Available":
            movie_name = movie_name.replace(f" {year}", "")

        # Get poster URL
        poster_url = await get_imdb(movie_name)

        # Create caption
        caption_message = (
            f"<b>Movie: <code>{movie_name}</code>\n\n"
            f"Year: {year}\n\n"
            f"Language: {language}\n\n"
            f"Quality: {quality}\n\n"
            f"📤 Uploading By: <a href='https://t.me/Movies_Dayz'>Movies Dayz</a>\n"
            f"⚡ Powered By: <a href='https://t.me/Star_Moviess_Tamil'>Star Movies Tamil</a></b>"
        )

        # Prepare buttons
        search_movie = movie_name.replace(" ", '-')
        btn = [
            [InlineKeyboardButton('📂 Get File 📂', url=f'https://telegram.me/{temp.U_NAME}?start=getfile-{search_movie}')],
            [InlineKeyboardButton('📥 How to Download 📥', url='https://t.me/How_downlode_dpbots/22')]
        ]
        reply_markup = InlineKeyboardMarkup(btn)

        # Send to channels
        for channel_id in channels:
            try:
                await bot.send_photo(
                    channel_id,
                    photo=poster_url,
                    caption=caption_message,
                    reply_markup=reply_markup
                )
            except Exception as e:
                print(f"Failed to send update to channel {channel_id}. Error: {e}")
                await bot.send_message(LOG_CHANNEL, f"Failed to send update to channel {channel_id}. Error: {e}")
    except Exception as e:
        print(f"Failed to send movie update. Error: {e}")
        await bot.send_message(LOG_CHANNEL, f"Failed to send movie update. Error: {e}")
        
