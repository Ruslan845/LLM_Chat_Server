from auth_app.models import User

class UserSerializer:
    @staticmethod
    def serialize_one(user):
        """Serialize a single user object."""
        return {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'social_auth': user.social_auth,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'avatar': user.avatar,
        }

    @staticmethod
    def serialize_many(users):
        """Serialize a list of user objects."""
        return [
            {
                'username': user.username,
                'social_auth': user.social_auth,
                'id': str(user.id),
                'is_admin': user.is_admin,
            }
            for user in users
        ]

    @staticmethod
    def validate_and_update(user, data):
        """
        Validate and update a user object with the provided data.
        :param user: The user object to update.
        :param data: A dictionary of fields to update.
        :return: The updated user object.
        """
        allowed_fields = ['username', 'email', 'social_auth', 'is_active', 'is_admin', 'avatar']
        errors = {}

        # Validate and update fields
        for field, value in data.items():
            if field in allowed_fields:
                if field == 'email' and not isinstance(value, str):
                    errors[field] = 'Invalid email format'
                else:
                    setattr(user, field, value)
            else:
                errors[field] = 'Field not allowed'

        if errors:
            return None, errors

        # Save the updated user
        user.save()
        return user, None

class ChatListSerializer:
    @staticmethod
    def serialize_one(chatlist):
        """Serialize a single user object."""
        return {
            'user_id': str(chatlist.user_id),
            'chat_id': str(chatlist.id),
            'chat_list': chatlist.chat_list,
        }
    
    @staticmethod
    def serialize_list(chat_list):
        return{
            'role': chat_list.get("role"),
            'text': chat_list.get("text"),
            'model': chat_list.get("model"),
            'date': chat_list.get("date").isoformat() if chat_list.get("date") else None,
            'deleteddate': chat_list.get("deleteddate").isoformat() if chat_list.get("deleteddate") else None,
        }

    @staticmethod
    def serialize_titlelist_one(chatlist):
        return {
            'chat_id': str(chatlist.get("chat_id")),
            'chat_title': chatlist.get("chat_title"),
        }
    
    @classmethod
    def serialize_titlelist_all(cls, data_list):
        return [cls.serialize_titlelist_one(item) for item in data_list]

    # user_id = me.ObjectIdField(required=True)
    # chat_number = me.IntField()
    # chat_list = me.ArrayField(default=[]) # number, text, model, date, deleteddate