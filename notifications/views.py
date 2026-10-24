from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    qs = Notification.objects.filter(user=request.user).select_related(
        "notification_type"
    )
    if request.GET.get("unread"):
        qs = qs.filter(is_read=False)
    page_obj = Paginator(qs, 30).get_page(request.GET.get("page"))
    return render(
        request,
        "notifications/notification_list.html",
        {
            "page_obj": page_obj,
            "notifications": page_obj.object_list,
            "unread_only": bool(request.GET.get("unread")),
        },
    )


@login_required
def notification_open(request, notification_id):
    """Marque comme lue puis redirige vers le lien de la notification."""
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user
    )
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])
    return redirect(notification.link or "notifications:notification_list")


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
    return redirect("notifications:notification_list")
