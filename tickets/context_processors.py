from django.utils import timezone
def user_roles(request):
    if request.user.is_authenticated:
        return {
            'is_customer': request.user.groups.filter(name='Customer').exists(),
            'is_agent': request.user.groups.filter(name='Support Agent').exists(),
            'is_admin': request.user.is_staff,
            "now": timezone.now(),
        }
    return {}