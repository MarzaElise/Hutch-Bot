from tortoise import fields
from tortoise.models import Model

class GuildModel(Model):

    id = fields.IntField(pk=True, description="Guild's id.")
    ai_chat_channel_id = fields.IntField(
        null=True,
        description="The channel id of the configured ai chat channel.",
    )
    is_blacklisted = fields.BooleanField(
        default=False,
        description="boolean field to mark if a guild with this id is blacklisted or not",
    )
    member: fields.ForeignKeyRelation["MemberModel"]
    automod_enabled = fields.BooleanField(default=True, description="Determines if automoderation should be enabled")    

    class Meta:
        table = "Guilds"

    def __str__(self) -> str:
        return "GuildModel(id={0.id}, ai_chat_channel_id={0.ai_chat_channel_id}, is_blacklisted={0.is_blacklisted})".format(self)
