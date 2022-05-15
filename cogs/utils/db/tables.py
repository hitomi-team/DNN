from cogs.utils.db.base import Base
import sqlalchemy as sa


class User(Base):
    __tablename__ = "users"
    user_id = sa.Column(sa.BigInteger, primary_key=True)


class UserAlias(Base):
    __tablename__ = "user_aliases"
    user_id = sa.Column(sa.ForeignKey("users.user_id"), primary_key=True)
    emoji_id = sa.Column(sa.ForeignKey("emotes.emote_id"), primary_key=True)
    alias = sa.Column(sa.String, nullable=False)


class Emote(Base):
    __tablename__ = "emotes"
    emoji_id = sa.Column(sa.BigInteger, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    animated = sa.Column(sa.Boolean, default=False, nullable=False)
    guild_id = sa.Column(sa.ForeignKey("guilds.guild_id"), nullable=False)


class Guild(Base):
    __tablename__ = "guilds"
    guild_id = sa.Column(sa.BigInteger, primary_key=True)
    prettify_jump_links = sa.Column(sa.Boolean, default=False, nullable=False)
    emote_sharing_enabled = sa.Column(sa.Boolean, default=False, nullable=False)


user_guild_association = sa.Table(
    'user_guild_association',
    Base.metadata,
    sa.Column("user_id", sa.ForeignKey("users.user_id")),
    sa.Column("guild_id", sa.ForeignKey("guilds.guild_id"))
)
