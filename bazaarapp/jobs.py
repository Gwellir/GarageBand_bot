from django.utils.timezone import now


class DeleteJob:
    def __init__(self, model, updater, intervals):
        self.model = model
        self.updater = updater
        self.intervals = intervals

    def __call__(self, *args, **kwargs):
        for interval in self.intervals:
            filter_ = dict(
                registered__created_at__lte=now() - interval.pop("before"),
                registered__created_at__gt=now() - interval.pop("after"),
                **interval,
            )
            selection = self.model.objects.filter(**filter_).order_by("-created_at")
            print(selection)
