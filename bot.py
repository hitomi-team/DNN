import logging
import traceback

import discord
from discord.ext import commands

from cogs.utils.config import BOT_TOKEN
from cogs.utils.dnn_cache import DNNCache

description = """
Allows you to send emojis from servers this bot is in.
"""

initial_cogs = (
    'cogs.emoji',
)


def _prefix_callable(bot, msg):
    user_id = bot.user.id
    return [f"<@!{user_id}> ", f"<@{user_id}> "]


class DNN(commands.AutoShardedBot):
    def __init__(self):
        logging.getLogger('discord').disabled = True

        intents = discord.Intents.all()

        super().__init__(
            command_prefix=_prefix_callable,
            description=description,
            pm_help=None,
            help_attrs=dict(hidden=True),
            intents=intents,
            status=discord.Status.dnd
        )

        self.dnn_cache = DNNCache()

        self.webhook_cache = {}

    async def setup_hook(self):
        for cog in initial_cogs:
            try:
                await self.load_extension(cog)

            except Exception:
                print(f"Failed to load cog {cog}.")
                traceback.print_exc()

    async def on_ready(self):
        print(f'Connected to Discord - ID: {self.user.id} - Shard: {self.shard_id}')

        self.dnn_cache.user_id = self.user.id

        for guild in self.guilds:
            self.dnn_cache.cache_guild(guild)

        print(f'Cached {len(self.dnn_cache.guild_cache)} guilds.')

    async def on_guild_join(self, guild):
        self.dnn_cache.cache_guild(guild)

    async def on_guild_remove(self, guild):
        self.dnn_cache.remove_guild(guild)

    async def on_guild_emojis_update(self, guild, before, after):
        self.dnn_cache.update_emojis(guild, before, after)

    async def on_member_join(self, member):
        self.dnn_cache.cache_member(member)

    async def on_member_remove(self, member):
        self.dnn_cache.remove_member(member)

    async def on_message(self, message):
        if message.author.bot:
            return

    async def start(self):
        await super().start(BOT_TOKEN, reconnect=True)

    async def close(self):
        await super().close()
