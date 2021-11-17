from tortoise import fields
from tortoise.models import Model
from .guilds import GuildModel


class MemberModel(Model):

    id = fields.IntField(pk=True, description="Id of the member")
    is_blacklisted = fields.BooleanField(
        default=False,
        description="a boolean field to store if this id is blacklisted",
    )
    is_opted_out = fields.BooleanField(
        default=False,
        description="Stores True if a member with this id is opted out of the dm command, defaults to False",
    )
    guild: fields.ForeignKeyRelation[GuildModel] = fields.ForeignKeyField(
        "models.GuildModel", related_name="member"
    )

    class Meta:
        table = "Members"

    def __str__(self) -> str:
        return "MemberModel(id={0.id}, is_blacklisted={0.is_blacklisted}, is_opted_out={0.is_opted_out})".format(self)
