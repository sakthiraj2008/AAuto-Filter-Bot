from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import INDEX_CHANNELS, ADMINS , LOG_CHANNEL, MOVIE_UPDATE_CHANNEL
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import get_poster, temp
import re
from database.users_chats_db import db

processed_movies = set()
media_filter = filters.document | filters.video

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
    return "https://telegra.ph/file/88d845b4f8a024a71465d.jpg"
    
async def movie_name_format(file_name):
  filename = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name).replace('_', ' ').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('{', '').replace('}', '').replace('.', ' ').replace('@', '').replace(':', '').replace(';', '').replace("'", '').replace('-', '').replace('!', '')).strip()
  return filename

async def check_qualities(text, qualities: list):
    quality = []
    for q in qualities:
        if q in text:
            quality.append(q)
    quality = ", ".join(quality)
    return quality[:-2] if quality.endswith(", ") else quality

async def check_languages(text, languages: list):
    matched_languages = []
    for lang in languages:
        if lang.lower() in text.lower():
            matched_languages.append(lang)
    result = " + ".join(matched_languages)
    return result[:-2] if result.endswith(" + ") else result

async def send_movie_updates(bot, file_name, caption, file_id):
    try:
        channels = await db.get_movie_update_channels()
        if not channels:
            channels = MOVIE_UPDATE_CHANNEL

        # Extract the year from the caption (if it exists)
        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else None

        # Extract the season information (if it exists)
        pattern = r"(?i)(?:s|season)0*(\d{1,2})"
        season = re.search(pattern, caption)
        if not season:
            season = re.search(pattern, file_name)
        
        # Set movie quality (if available)
        qualities = ["hdcam", "HDCAM", "HDRip", "hdrip", "SDTV", "sdtv", "HDTV", "HDTV", "BluRay", "bluray", "HD DVD", "hd dvd",
                     "camrip", "WEB-DL", "CAMRip", "hdtc", "PreDVD", "DVDscr", "dvdscr", "WEB-HD", "web-hd", "BDRip", "bdrip",
                     "dvdrip", "dvdscr", "HDTC", "dvdscreen", "HDTS", "hdts"]
        quality = await check_qualities(caption, qualities) or "HDRip"

        # Detect language (including abbreviations)
        nb_languages = {
            "Tamil": ["Tamil", "Tam", "Tami", "Tml"],
            "Bengali": ["Bengali", "Ben", "Bng"],
            "English": ["English", "Eng", "Engl", "En"],
            "Marathi": ["Marathi", "Mar", "Mrt"],
            "Hindi": ["Hindi", "Hin", "Hind"],
            "Telugu": ["Telugu", "Tel", "Telg"],
            "Malayalam": ["Malayalam", "Mal", "Mly"],
            "Kannada": ["Kannada", "Kan", "Knd"],
            "Punjabi": ["Punjabi", "Pnj", "Pun"],
            "Gujarati": ["Gujarati", "Guj", "Gujr"],
            "Korean": ["Korean", "Kor", "Krn"],
            "Japanese": ["Japanese", "Jap", "Jpn"],
            "Bhojpuri": ["Bhojpuri", "Bjp", "Bjpuri"],
            "Chinese": ["Chinese", "Ch", "Chn"],
            "Dual": ["Dual", "Dbl", "Dul"],
            "Multi": ["Multi", "Mlti", "Mlt"]
        }

        languages = await check_languages(caption, nb_languages) or "Not Idea"
        # Format movie name
        movie_name = await movie_name_format(file_name)
        if movie_name in processed_movies:
            return
        processed_movies.add(movie_name)
        movie = await movie_name_format(file_name)
        if year:
            movie = movie.replace(f" {year}", "")
        poster_url = await get_imdb(movie)
        caption_message = f"<b>Movie :- <code>{movie}</code>\n\nYear :- {year if year else 'Not Available'}\n\nLanguage :- {language}\n\nQuality :- {quality.replace(', ', ' ')}\n\n📤 Uploading By :- <a href=https://t.me/Movies_Dayz>Movies Dayz</a>\n\n⚡ Powered By :- <a href=https://t.me/Star_Moviess_Tamil>Star Movies Tamil</a></b>"
        search_movie = movie.replace(" ", '-')
        if year:
            search_movie = search_movie.replace(f"-{year}", "")

        # Buttons for channels
        btn = [[
            InlineKeyboardButton('📂 Get File 📂', url=f'https://telegram.me/{temp.U_NAME}?start=getfile-{search_movie}')
        ], [
            InlineKeyboardButton('📥 How to Download 📥', url=f'https://t.me/How_downlode_dpbots/22')
        ]]
        reply_markup = InlineKeyboardMarkup(btn)

        # Send to all channels
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
