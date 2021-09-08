from time import sleep

from django.utils.timezone import now


class DeleteJob:
    def __init__(self, model, updater, intervals):
        self.model = model
        self.updater = updater
        self.intervals = intervals

    def __call__(self, *args, **kwargs):
        for interval in self.intervals:
            i_ = interval.copy()
            filter_ = dict(
                registered__created_at__lte=now() - i_.pop("before"),
                registered__created_at__gt=now() - i_.pop("after"),
                **i_,
            )
            selection = self.model.objects.filter(**filter_).order_by("-created_at")
            for ad in selection:
                ad.delete_post()
                sleep(60)
