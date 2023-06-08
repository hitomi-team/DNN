import re

import discord
from discord.ext import commands

BLURPLE_COLOR = discord.Color(value=0x5865f2)

EMOJI_REGEX = re.compile(r'\<[^>]*\>')
NON_EMOJI_REGEX = re.compile(r'\:([a-zA-Z0-9_]+)\:')
MSG_LINK_REGEX = re.compile(r'https://discord.com/channels/(\d+)/(\d+)/(\d+)')


class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def clean_emojis(self, msg):
        emoji_matches = re.findall(EMOJI_REGEX, msg)
        filtered_content = ''

        if not emoji_matches:
            filtered_content = msg

        for match in emoji_matches:
            filtered_content = filtered_content.replace(match, '')

        return filtered_content
    
    def get_avatar(self, msg):
        # people with default avatars will have a null avatar_url
        if msg.author.avatar is not None:
            return msg.author.avatar.url
        else:
            return None

    @commands.Cog.listener("on_message")
    async def on_message(self, msg):
        if msg.guild is None or msg.author.bot:
            return

        # check if guild has a bot named NQN, if it does, don't process
        if msg.guild.get_member(559426966151757824):
            return

        webhook = await self.bot.dnn_cache.get_or_create_webhook(msg.channel)

        # regex to check if message has a link like https://discord.com/channels/guild_id/channel_id/message_id
        msg_link_match = re.search(MSG_LINK_REGEX, msg.content)

        if msg_link_match:
            await msg.delete()
            
            guild_id = msg_link_match.group(1)
            channel_id = msg_link_match.group(2)
            message_id = msg_link_match.group(3)
            
            if (guild_id not in self.bot.dnn_cache.guild_cache) or (not self.bot.dnn_cache.guild_cache[guild_id]['users'][msg.author.id]):
                return # user does not have access to guild

            channel = self.bot.get_channel(int(channel_id))

            if channel is None:
                return

            ref_message = await channel.fetch_message(int(message_id))

            if ref_message is None:
                return

            embed = discord.Embed(title='Jump to message', url=ref_message.jump_url, color=BLURPLE_COLOR)

            # check for attachments
            if ref_message.attachments:
                embed.set_image(url=ref_message.attachments[0].url)

            embed.description = ref_message.content
            embed.set_author(
                name=ref_message.author.name,
                icon_url=self.get_avatar(ref_message),
            )
            embed.set_footer(text=f'#{ref_message.channel.name}')

            msgtext = msg.content.replace(msg_link_match.group(0), f"[message link]({msg_link_match.group(0)})") if not msg.content == msg_link_match.group(0) else ""

            await webhook.send(
                content=msgtext,
                embed=embed,
                username=msg.author.name,
                avatar_url=self.get_avatar(msg),
            )

        filtered_content = self.clean_emojis(msg.content)
        non_emoji_matches = re.findall(NON_EMOJI_REGEX, filtered_content)

        if not non_emoji_matches:
            return

        new_msg = msg.content
        replaced = False

        for non_emoji in non_emoji_matches:
            emoji = self.bot.dnn_cache.get_emoji(msg.guild.id, msg.author.id, non_emoji)

            if emoji is not None:
                new_msg = new_msg.replace(
                    f":{non_emoji}:",
                    f"<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>"
                )

                replaced = True

        if not replaced:
            return

        await msg.delete()

        if msg.reference is not None:
            # create embed with message reference
            message_id = msg.reference.message_id
            ref_message = await msg.channel.fetch_message(message_id)
            embed = discord.Embed(title='Jump to message', url=msg.reference.jump_url, color=BLURPLE_COLOR)

            if ref_message:
                embed.description = ref_message.content

                # check for attachments
                if ref_message.attachments:
                    embed.set_image(url=ref_message.attachments[0].url)
            
            embed.set_author(name=ref_message.author.name, icon_url=self.get_avatar(ref_message))
            await webhook.send(content=new_msg, embed=embed, username=msg.author.name, avatar_url=self.get_avatar(msg))

        else:
            await webhook.send(new_msg, username=msg.author.name, avatar_url=self.get_avatar(msg))
        
async def setup(bot):
    await bot.add_cog(Emoji(bot))
