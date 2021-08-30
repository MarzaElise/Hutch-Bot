from tortoise import fields
from tortoise.models import Model


class GuildModel(Model):

    id = fields.IntField(pk=True, description="Guild's id.")
    ai_chat_channel_id = fields.IntField(
        null=True, description="The channel id of the configured ai chat channel."
    )
    is_blacklisted = fields.BooleanField(
        default=False,
        description="boolean field to mark if a guild with this id is blacklisted or not",
    )

    class Meta:
        table = "Guilds"
