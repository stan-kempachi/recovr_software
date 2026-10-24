from .services import unread_count


def notifications(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"unread_notifications_count": 0}
    return {"unread_notifications_count": unread_count(user)}
