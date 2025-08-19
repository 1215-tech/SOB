import logging

logger = logging.getLogger(__name__)

def get_user_info(user):
    """Returns a string with user information."""
    return f"{user.full_name} (@{user.username}, {user.id})"
