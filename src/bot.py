import logging
import traceback

import discord
from discord.ext import commands

import config

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

        self.webhook_cache = {}
        self.guild_cache = {}
        self.emoji_cache = {}

    async def setup_hook(self):
        for cog in initial_cogs:
            try:
                await self.load_extension(cog)

            except Exception:
                print(f"Failed to load cog {cog}.")
                traceback.print_exc()

    async def on_ready(self):
        print(f'Connected to Discord - ID: {self.user.id} - Shard: {self.shard_id}')

        for guild in self.guilds:
            await self.cache_guild(guild)

        print(f'Cached {len(self.guild_cache)} guilds.')

    async def ensure_webhook(self, channel):
        if channel.id in self.webhook_cache:
            return self.webhook_cache[channel.id]

        for webhook in await channel.webhooks():
            if webhook.user.id == self.user.id:
                self.webhook_cache[channel.id] = webhook
                return webhook

        if channel.id in self.webhook_cache:
            return self.webhook_cache[channel.id]

        new_webhook = await channel.create_webhook(name='DNN Webhook')
        self.webhook_cache[channel.id] = new_webhook

        return new_webhook

    async def cache_guild(self, guild):
        # guild_id: {'users': [], 'emojis': []}
        if guild.id in self.guild_cache:
            return

        self.guild_cache[guild.id] = {'users': set(), 'emojis': {}}

        for user in guild.members:
            self.guild_cache[guild.id]['users'].add(user.id)

        for emoji in guild.emojis:
            self.guild_cache[guild.id]['emojis'][emoji.name] = emoji

    async def on_guild_join(self, guild):
        await self.cache_guild(guild)

    async def on_guild_remove(self, guild):
        if guild.id in self.guild_cache:
            del self.guild_cache[guild.id]

    async def on_guild_emojis_update(self, guild, before, after):
        if guild.id not in self.guild_cache:
            return

        self.guild_cache[guild.id]['emojis'] = {}

        for emoji in after:
            if emoji not in self.guild_cache[guild.id]['emojis']:
                self.guild_cache[guild.id]['emojis'][emoji.name] = emoji

    async def on_member_join(self, member):
        self.guild_cache[member.guild.id]['users'].append(member.id)

    async def on_message(self, message):
        if message.author.bot:
            return

    async def start(self):
        await super().start(config.token, reconnect=True)

    async def close(self):
        await super().close()

    @property
    def config(self):
        return __import__("config")
