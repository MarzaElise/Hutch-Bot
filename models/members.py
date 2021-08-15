from tortoise import fields
from tortoise.models import Model


class MembeModel(Model):

    id: fields.IntField(pk=True, description="Id of the member")
    is_blacklisted: fields.BooleanField(
        default=False, description="a boolean field to store if this id is blacklisted"
    )
    is_opted_out: fields.BooleanField(
        default=False,
        description="Stores True if a member with this id is opted out of the dm command, defaults to False",
    )
    class Meta:
        table = "Members"
