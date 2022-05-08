import re
import asyncio
import logging
import discord

class DNNClient:
    def __init__(self, config):
        self.token = config['discord_token']
        logging.getLogger('discord').disabled = True

        intents = discord.Intents.all()
        self.client = discord.AutoShardedClient(intents=intents, status=discord.Status.dnd)
        self.webhook_cache = {}
        self.guild_cache = {}
        self.emoji_cache = {}

    def run(self):
        print('Starting Discord Client.')
        self.on_ready = self.client.event(self.on_ready)
        self.on_message = self.client.event(self.on_message)

        self.client.run(self.token)
    
    def close(self):
        asyncio.run(self.client.close())
    
    async def on_ready(self):
        print(f'Connected to Discord - ID: {self.client.user.id} - Shard: {self.client.shard_id}')
        for guild in self.client.guilds:
            await self.cache_guild(guild)
        print(f'Cached {len(self.guild_cache)} guilds.')
    
    async def ensure_webhook(self, channel):
        if channel.id in self.webhook_cache:
            return self.webhook_cache[channel.id]
        for webhook in await channel.webhooks():
            if webhook.user.id == self.client.user.id:
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
        self.guild_cache[guild.id] = {'users': [], 'emojis': []}
        for user in guild.members:
            self.guild_cache[guild.id]['users'].append(user.id)
        for emoji in guild.emojis:
            self.guild_cache[guild.id]['emojis'].append(emoji)
    
    async def on_guild_join(self, guild):
        await self.cache_guild(guild)
    
    async def on_guild_remove(self, guild):
        if guild.id in self.guild_cache:
            del self.guild_cache[guild.id]
    
    async def on_guild_emojis_update(self, guild, before, after):
        if guild.id not in self.guild_cache:
            return
        for emoji in after:
            if emoji not in self.guild_cache[guild.id]['emojis']:
                self.guild_cache[guild.id]['emojis'].append(emoji)
        
    async def on_member_join(self, member):
        self.guild_cache[member.guild.id]['users'].append(member.id)

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.cache_guild(message.guild)
        real_emoji_matches = re.findall(r'\<[^>]*\>', message.content)
        filtered_content = ''
        if not real_emoji_matches:
            filtered_content = message.content
        for match in real_emoji_matches:
            filtered_content = filtered_content.replace(match, '')
        non_emoji_matches = re.findall(r'\:([a-zA-Z0-9_]+)\:', filtered_content)
        if not non_emoji_matches:
            return

        new_msg = message.content

        for non_emoji in non_emoji_matches:
            # replace non_emoji from :helpme: to <:helpme:717> or <a:helpme:717> if it's an animated emoji
            # only replace emoji if user is in guild that has the emoji
            for g_id in self.guild_cache:
                if message.author.id in self.guild_cache[g_id]['users']:
                    for emoji in self.guild_cache[g_id]['emojis']:
                        if emoji.name.lower() == non_emoji.lower():
                            if emoji.animated:
                                new_msg = new_msg.replace(f':{non_emoji}:', f'<a:{emoji.name}:{emoji.id}>')
                            else:
                                new_msg = new_msg.replace(f':{non_emoji}:', f'<:{emoji.name}:{emoji.id}>')
            
        if new_msg == message.content:
            return
            
        webhook = await self.ensure_webhook(message.channel)
        await message.delete()
        await webhook.send(new_msg, username=message.author.name, avatar_url=message.author.avatar.url)