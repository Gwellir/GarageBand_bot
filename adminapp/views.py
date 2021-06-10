from django.contrib.auth.decorators import user_passes_test


@user_passes_test(lambda u: u.is_superuser, login_url="admin:login")
def logs_list_view(request, pk):
    pass
