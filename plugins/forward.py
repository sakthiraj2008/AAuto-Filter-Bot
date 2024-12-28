import logging
import re
import asyncio
from datetime import datetime
from telethon import TelegramClient, events, Button, sync
from telethon.sessions import StringSession
from telethon.tl.types import PeerChannel, PeerChat, PeerUser
from telethon.utils import get_display_name
from telethon.tl.functions.users import GetFullUserRequest
from info import USER_STRING_SESSION, API_ID, API_HASH, SOURCE_CHANNELS1, SOURCE_CHANNELS2, SOURCE_CHANNELS3, SOURCE_CHANNELS4, SOURCE_CHANNELS5, SOURCE_CHANNELS6, SOURCE_CHANNELS7, ADMINS
from database.users_chats_db import db

# Setting up logging
logger = logging.getLogger(__name__)
try:
    user_client = TelegramClient(StringSession(USER_STRING_SESSION), API_ID, API_HASH)
    await user_client.start()
except Exception as e:
    logger.error(f"Error initializing the bot: {str(e)}")
    logger.error("Bot is quitting...")
    exit()

@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS1))  # Listen to the source_channel (list of channels)
async def forward_message(event, command_type=1):
    user_id = event.sender_id

    # Ignore the "Bot Started!" message
    if event.message.text == "Bot Started!":
        return

    # Fetch the channel configuration based on command_type
    channel_data = db.get_channel(command_type)
    if not channel_data:
        logger.error(f"No data found for command_type: {command_type}")
        return

    # Extract data from the channel configuration
    destination_channels = channel_data.get("destination_channel_ids", [])
    original_text = channel_data.get("original_text", "")
    replace_text = channel_data.get("replace_text", "")
    my_link = channel_data.get("my_link", "")
    web_link = channel_data.get("web_link", "")
    my_username = channel_data.get("my_username", "")

    if not destination_channels:
        logger.warning(f"No destination channels found for command_type {command_type}")
        return

    logger.info(f"Handling command_type {command_type}: destination_channels={destination_channels}")

    # Handle media messages
    if event.message.media:
        if getattr(event.message, 'message', None):  # Check if message has caption
            replaced_caption = await replace_links_in_caption(
                event.message.message, web_link, my_link, my_username, original_text, replace_text
            )
            event.message.message = replaced_caption

        # Send the message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, event.message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

    else:
        # Handle text-only messages (replace links and text)
        replaced_message = await replace_links_in_message(
            event.message.text, web_link, my_link, my_username, original_text, replace_text
        )

        # Send the replaced message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, replaced_message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS2))  # Listen to the source_channel (list of channels)
async def forward_message(event, command_type=2):
    user_id = event.sender_id

    # Ignore the "Bot Started!" message
    if event.message.text == "Bot Started!":
        return

    # Fetch the channel configuration based on command_type
    channel_data = db.get_channel(command_type)
    if not channel_data:
        logger.error(f"No data found for command_type: {command_type}")
        return

    # Extract data from the channel configuration
    destination_channels = channel_data.get("destination_channel_ids", [])
    original_text = channel_data.get("original_text", "")
    replace_text = channel_data.get("replace_text", "")
    my_link = channel_data.get("my_link", "")
    web_link = channel_data.get("web_link", "")
    my_username = channel_data.get("my_username", "")

    if not destination_channels:
        logger.warning(f"No destination channels found for command_type {command_type}")
        return

    logger.info(f"Handling command_type {command_type}: destination_channels={destination_channels}")

    # Handle media messages
    if event.message.media:
        if getattr(event.message, 'message', None):  # Check if message has caption
            replaced_caption = await replace_links_in_caption(
                event.message.message, web_link, my_link, my_username, original_text, replace_text
            )
            event.message.message = replaced_caption

        # Send the message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, event.message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

    else:
        # Handle text-only messages (replace links and text)
        replaced_message = await replace_links_in_message(
            event.message.text, web_link, my_link, my_username, original_text, replace_text
        )

        # Send the replaced message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, replaced_message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS3))  # Listen to the source_channel (list of channels)
async def forward_message(event, command_type=3):
    user_id = event.sender_id

    # Ignore the "Bot Started!" message
    if event.message.text == "Bot Started!":
        return

    # Fetch the channel configuration based on command_type
    channel_data = db.get_channel(command_type)
    if not channel_data:
        logger.error(f"No data found for command_type: {command_type}")
        return

    # Extract data from the channel configuration
    destination_channels = channel_data.get("destination_channel_ids", [])
    original_text = channel_data.get("original_text", "")
    replace_text = channel_data.get("replace_text", "")
    my_link = channel_data.get("my_link", "")
    web_link = channel_data.get("web_link", "")
    my_username = channel_data.get("my_username", "")

    if not destination_channels:
        logger.warning(f"No destination channels found for command_type {command_type}")
        return

    logger.info(f"Handling command_type {command_type}: destination_channels={destination_channels}")

    # Handle media messages
    if event.message.media:
        if getattr(event.message, 'message', None):  # Check if message has caption
            replaced_caption = await replace_links_in_caption(
                event.message.message, web_link, my_link, my_username, original_text, replace_text
            )
            event.message.message = replaced_caption

        # Send the message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, event.message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

    else:
        # Handle text-only messages (replace links and text)
        replaced_message = await replace_links_in_message(
            event.message.text, web_link, my_link, my_username, original_text, replace_text
        )

        # Send the replaced message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, replaced_message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS4))  # Listen to the source_channel (list of channels)
async def forward_message(event, command_type=4):
    user_id = event.sender_id

    # Ignore the "Bot Started!" message
    if event.message.text == "Bot Started!":
        return

    # Fetch the channel configuration based on command_type
    channel_data = db.get_channel(command_type)
    if not channel_data:
        logger.error(f"No data found for command_type: {command_type}")
        return

    # Extract data from the channel configuration
    destination_channels = channel_data.get("destination_channel_ids", [])
    original_text = channel_data.get("original_text", "")
    replace_text = channel_data.get("replace_text", "")
    my_link = channel_data.get("my_link", "")
    web_link = channel_data.get("web_link", "")
    my_username = channel_data.get("my_username", "")

    if not destination_channels:
        logger.warning(f"No destination channels found for command_type {command_type}")
        return

    logger.info(f"Handling command_type {command_type}: destination_channels={destination_channels}")

    # Handle media messages
    if event.message.media:
        if getattr(event.message, 'message', None):  # Check if message has caption
            replaced_caption = await replace_links_in_caption(
                event.message.message, web_link, my_link, my_username, original_text, replace_text
            )
            event.message.message = replaced_caption

        # Send the message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, event.message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

    else:
        # Handle text-only messages (replace links and text)
        replaced_message = await replace_links_in_message(
            event.message.text, web_link, my_link, my_username, original_text, replace_text
        )

        # Send the replaced message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, replaced_message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS5))  # Listen to the source_channel (list of channels)
async def forward_message(event, command_type=5):
    user_id = event.sender_id

    # Ignore the "Bot Started!" message
    if event.message.text == "Bot Started!":
        return

    # Fetch the channel configuration based on command_type
    channel_data = db.get_channel(command_type)
    if not channel_data:
        logger.error(f"No data found for command_type: {command_type}")
        return

    # Extract data from the channel configuration
    destination_channels = channel_data.get("destination_channel_ids", [])
    original_text = channel_data.get("original_text", "")
    replace_text = channel_data.get("replace_text", "")
    my_link = channel_data.get("my_link", "")
    web_link = channel_data.get("web_link", "")
    my_username = channel_data.get("my_username", "")

    if not destination_channels:
        logger.warning(f"No destination channels found for command_type {command_type}")
        return

    logger.info(f"Handling command_type {command_type}: destination_channels={destination_channels}")

    # Handle media messages
    if event.message.media:
        if getattr(event.message, 'message', None):  # Check if message has caption
            replaced_caption = await replace_links_in_caption(
                event.message.message, web_link, my_link, my_username, original_text, replace_text
            )
            event.message.message = replaced_caption

        # Send the message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, event.message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

    else:
        # Handle text-only messages (replace links and text)
        replaced_message = await replace_links_in_message(
            event.message.text, web_link, my_link, my_username, original_text, replace_text
        )

        # Send the replaced message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, replaced_message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS6))  # Listen to the source_channel (list of channels)
async def forward_message(event, command_type=6):
    user_id = event.sender_id

    # Ignore the "Bot Started!" message
    if event.message.text == "Bot Started!":
        return

    # Fetch the channel configuration based on command_type
    channel_data = db.get_channel(command_type)
    if not channel_data:
        logger.error(f"No data found for command_type: {command_type}")
        return

    # Extract data from the channel configuration
    destination_channels = channel_data.get("destination_channel_ids", [])
    original_text = channel_data.get("original_text", "")
    replace_text = channel_data.get("replace_text", "")
    my_link = channel_data.get("my_link", "")
    web_link = channel_data.get("web_link", "")
    my_username = channel_data.get("my_username", "")

    if not destination_channels:
        logger.warning(f"No destination channels found for command_type {command_type}")
        return

    logger.info(f"Handling command_type {command_type}: destination_channels={destination_channels}")

    # Handle media messages
    if event.message.media:
        if getattr(event.message, 'message', None):  # Check if message has caption
            replaced_caption = await replace_links_in_caption(
                event.message.message, web_link, my_link, my_username, original_text, replace_text
            )
            event.message.message = replaced_caption

        # Send the message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, event.message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

    else:
        # Handle text-only messages (replace links and text)
        replaced_message = await replace_links_in_message(
            event.message.text, web_link, my_link, my_username, original_text, replace_text
        )

        # Send the replaced message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, replaced_message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

@user_client.on(events.NewMessage(chats=SOURCE_CHANNELS7))  # Listen to the source_channel (list of channels)
async def forward_message(event, command_type=7):
    user_id = event.sender_id

    # Ignore the "Bot Started!" message
    if event.message.text == "Bot Started!":
        return

    # Fetch the channel configuration based on command_type
    channel_data = db.get_channel(command_type)
    if not channel_data:
        logger.error(f"No data found for command_type: {command_type}")
        return

    # Extract data from the channel configuration
    destination_channels = channel_data.get("destination_channel_ids", [])
    original_text = channel_data.get("original_text", "")
    replace_text = channel_data.get("replace_text", "")
    my_link = channel_data.get("my_link", "")
    web_link = channel_data.get("web_link", "")
    my_username = channel_data.get("my_username", "")

    if not destination_channels:
        logger.warning(f"No destination channels found for command_type {command_type}")
        return

    logger.info(f"Handling command_type {command_type}: destination_channels={destination_channels}")

    # Handle media messages
    if event.message.media:
        if getattr(event.message, 'message', None):  # Check if message has caption
            replaced_caption = await replace_links_in_caption(
                event.message.message, web_link, my_link, my_username, original_text, replace_text
            )
            event.message.message = replaced_caption

        # Send the message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, event.message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")

    else:
        # Handle text-only messages (replace links and text)
        replaced_message = await replace_links_in_message(
            event.message.text, web_link, my_link, my_username, original_text, replace_text
        )

        # Send the replaced message to each destination channel
        for destination_channel_id in destination_channels:
            try:
                # Ensure destination_channel_id is an integer (if needed)
                destination_channel_id = int(destination_channel_id)

                # Try to get the entity using the destination channel ID
                #destination_channel = await event.client.get_entity(destination_channel_id)
                await event.client.send_message(destination_channel_id, replaced_message)
                logger.info(f"Message forwarded to {destination_channel_id}")
            except ValueError as e:
                logger.error(f"Invalid entity ID for {destination_channel_id}: {e}")
            except Exception as e:
                logger.error(f"Failed to forward message to {destination_channel_id}: {e}")
                

async def replace_links_in_message(message, web_link, my_link, my_username, original_text, replace_text):
    if web_link:
        message = re.sub(r'https?://tcvvip5\.com/#/register\?r_code=44YWW823408', web_link, message)
    if my_link:
        message = re.sub(r'https?://t\.me\S*|t\.me\S*', my_link, message)
    if my_username:
        message = re.sub(r'@[\w]+', my_username, message)
    message = message.replace(original_text, replace_text)
    return message

async def replace_links_in_caption(caption, web_link, my_link, my_username, original_text, replace_text):
    if web_link:
        caption = re.sub(r'https?://tcvvip5\.com/#/register\?r_code=44YWW823408', web_link, caption)
    if my_link:
        caption = re.sub(r'https?://t\.me\S*|t\.me\S*', my_link, caption)
    if my_username:
        caption = re.sub(r'@[\w]+', my_username, caption)
    caption = caption.replace(original_text, replace_text)
    return caption
  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(user_client.start())
    
