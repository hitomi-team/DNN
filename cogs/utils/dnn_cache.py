class DNNCache:
    def __init__(self):
        self.user_id = None
        self.webhook_cache = {}
        self.guild_cache = {}

    def remove_guild(self, guild):
        if guild.id in self.guild_cache:
            del self.guild_cache[guild.id]

    def cache_guild(self, guild):
        if guild.id in self.guild_cache:
            return

        self.guild_cache[guild.id] = {}
        self.guild_cache[guild.id]["users"] = set()
        self.guild_cache[guild.id]["emojis"] = {}

        for user in guild.members:
            self.guild_cache[guild.id]["users"].add(user.id)

        for emoji in guild.emojis:
            self.guild_cache[guild.id]["emojis"][emoji.name] = emoji

    def cache_webhook(self, channel, webhook):
        self.webhook_cache[channel.id] = webhook

    async def get_webhook(self, channel):
        if channel.id in self.webhook_cache:
            return self.webhook_cache[channel.id]

        for webhook in await channel.webhooks():
            if webhook.user.id == self.user_id:
                self.webhook_cache[channel.id] = webhook
                return webhook

        return None

    async def get_or_create_webhook(self, channel):
        webhook = await self.get_webhook(channel)

        if webhook is None:
            webhook = await channel.create_webhook(name="DNN Webhook")
            self.webhook_cache[channel.id] = webhook

        return webhook

    def update_emojis(self, guild, before, after):
        if guild.id not in self.guild_cache:
            return

        self.guild_cache[guild.id]["emojis"] = {}

        for emoji in after:
            if emoji not in self.guild_cache[guild.id]["emojis"]:
                self.guild_cache[guild.id]["emojis"][emoji.name] = emoji

    def remove_member(self, member):
        if member.id in self.guild_cache[member.guild.id]:
            self.guild_cache[member.guild.id].remove(member.id)

    def cache_member(self, member):
        self.guild_cache[member.guild.id]["users"].add(member.id)

    def get_emoji(self, guild_id, user_id, emoji_name):
        for guild in self.guild_cache:
            guild = self.guild_cache[guild]

            if user_id in guild["users"] and emoji_name in guild["emojis"]:
                return guild["emojis"][emoji_name]

        return None
