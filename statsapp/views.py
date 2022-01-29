from collections import Counter

from django.apps import apps
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.shortcuts import render

from tgbot.models import BotUser, MessengerBot


@user_passes_test(lambda u: u.is_superuser, login_url="admin:login")
def stats_main(request, debug=0):
    """
    Отображает список пользователей, диалогов выбранного пользователя и
    содержимое выбранного диалога.

    :type request: :class:`django.http.HttpRequest`
    :type debug: int
    """

    bot_list = []
    for bot in (
        MessengerBot.objects.filter(is_debug=debug, is_active=True)
        .exclude(bound_object__icontains="filter")
        .select_related()
    ):
        model = apps.get_model(bot.bound_app, bot.bound_object)
        related_name = model._meta.get_field("user").related_query_name()
        users_kwargs = {
            f"{related_name}__isnull": False,
            f"{related_name}__dialog__bot": bot,
        }
        users_q = BotUser.objects.filter(**users_kwargs).distinct().select_related()
        total_users = users_q.count()
        have_posts_kwargs = {
            f"{related_name}__is_complete": True,
            f"{related_name}__dialog__bot": bot,
        }
        users_with_posts_q = BotUser.objects.filter(**have_posts_kwargs).distinct()
        users_with_posts = users_with_posts_q.count()
        posts_per_user_kwargs = {f"{related_name}__registered_posts__isnull": False}
        posts_per_user = (
            BotUser.objects.filter(**have_posts_kwargs, **posts_per_user_kwargs)
            .annotate(count=Count(f"{related_name}__id"))
            .order_by("-count")
            .values("id", "name", "user_id", "count")[:10]
        )

        objs_q = model.objects.filter(dialog__bot=bot)
        dropped_objs_q = objs_q.filter(is_complete=False)
        stages_stats = dropped_objs_q.values("stage__id", "stage__name")
        count = Counter(
            [
                (stage.get("stage__id"), stage.get("stage__name"))
                for stage in stages_stats
            ]
        )

        bot_list.append(
            dict(
                number=bot.pk,
                name=bot.name,
                model=model,
                total_users=total_users,
                users_with_posts=users_with_posts,
                posts_per_user=posts_per_user,
                stages_stats=sorted(
                    list(count.items()),
                    key=lambda item: item[0][0] if item[0][0] else 0,
                ),
            )
        )

    context = {
        "title_page": "Статистика",
        "bot_list": bot_list,
    }

    return render(request, "statsapp/stats_view.html", context)
