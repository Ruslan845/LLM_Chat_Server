import mongoengine as me

class User(me.Document):
    username = me.StringField(required=True, unique=True)
    email = me.EmailField(required=True, unique=True)
    social_auth = me.DictField()  # Store social auth details
    is_active = me.BooleanField(default=True)
    created_at = me.DateTimeField(auto_now_add=True)
    is_admin = me.BooleanField(default=False)
    models = me.ListField(default=["gpt-4o","gpt-4-turbo","gpt-3.5-turbo","text-davinci-003","DeepSeek-V3","DeepSeek-R1"])
    avatar = me.StringField()

class Chatlist(me.Document):
    user_id = me.ObjectIdField(required=True)
    # number = me.IntField()
    # chat_category = me.StringField(max_length=50)
    chat_list = me.ListField(default=[]) # number, text, model, date, deleteddate
    chat_title = me.StringField(required=False)
    # auth = me.BooleanField(default = False)
    is_deleted = me.BooleanField(default = False)

class APIKey(me.Document):
    name = me.StringField(required=True, unique=True)
    value = me.StringField(required=True, unique=True)