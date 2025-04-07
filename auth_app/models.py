import mongoengine as me

class User(me.Document):
    username = me.StringField(required=True, unique=True)
    email = me.EmailField(required=True, unique=True)
    social_auth = me.DictField()  # Store social auth details
    is_active = me.BooleanField(default=True)
    created_at = me.DateTimeField(auto_now_add=True)
    is_admin = me.BooleanField(default=False)
    avatar = me.StringField()