"""Initial table setup

Revision ID: 6980624f7a75
Revises:
Create Date: 2022-05-14 16:44:20.046704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6980624f7a75'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("user_id", sa.BigInteger, primary_key=True)
    )

    op.create_table(
        "user_guild_association",
        sa.Column("user_id", sa.ForeignKey("users.user_id")),
        sa.Column("guild_id", sa.ForeignKey("guilds.guild_id"))
    )

    op.create_table(
        "user_aliases",
        sa.Column("user_id", sa.ForeignKey("users.user_id")),
        sa.Column("emoji_id", sa.ForeignKey("emotes.emote_id")),
        sa.Column("alias", sa.String, nullable=False)
    )

    op.create_primary_key(
        "pk_user_aliases",
        "user_aliases",
        ["user_id", "emoji_id"]
    )

    op.create_table(
        "emotes",
        sa.Column("emoji_id", sa.BigInteger, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("animated", sa.Boolean, default=False, nullable=False),
        sa.Column("guild_id", sa.ForeignKey("guilds.guild_id"), nullable=False)
    )

    op.create_table(
        "guilds",
        sa.Column("guild_id", sa.BigInteger, primary_key=True),
        sa.Column("prettify_jump_links", sa.Boolean, default=False, nullable=False),
        sa.Column("emote_sharing_enabled", sa.Boolean, default=False, nullable=False)
    )


def downgrade():
    pass
