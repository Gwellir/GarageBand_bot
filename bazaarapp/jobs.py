from time import sleep

from django.utils.timezone import now

from logger.log_config import BOT_LOG


class ReminderJob:
    def __init__(self, model, updater, intervals):
        self.model = model
        self.updater = updater
        self.intervals = intervals

    def __call__(self, *args, **kwargs):
        BOT_LOG.info("Reminders triggered")
        for interval in self.intervals:
            i_ = interval.copy()
            day_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
            filter_ = dict(
                registered_posts__created_at__lte=day_start - i_.pop("before"),
                registered_posts__created_at__gt=day_start - i_.pop("after"),
                **i_,
            )
            selection = self.model.objects.filter(**filter_).order_by("-created_at")
            for ad in selection:
                ad.registered.propose_renewal()
                sleep(0.2)
