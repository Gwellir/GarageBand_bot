import copy

from django.db import models


class TrackableUpdateCreateModel(models.Model):
    """
    Базовый компонент модели
    с полями для отслеживания времени создания и обновления.
    """

    created_at = models.DateTimeField(
        verbose_name="Время создания", auto_now_add=True, db_index=True
    )
    updated_at = models.DateTimeField(
        verbose_name="Время последней активности", auto_now=True, db_index=True
    )

    class Meta:
        abstract = True


class LocationRegionBindModel(models.Model):
    """
    Базовый компонент модели для отслеживания локаций в заявках.
    """

    location_desc = models.CharField(
        verbose_name="Описание местоположения", blank=True, max_length=100
    )
    location_key = models.ForeignKey(
        "tgbot.Location", on_delete=models.SET_NULL, null=True
    )

    class Meta:
        abstract = True

    def select_location_by_input(self, user_input, fk_model):
        selection = fk_model.objects.filter(name__iexact=user_input)
        if not selection:
            selection = fk_model.objects.filter(name__icontains=user_input)
        if not selection:
            selection = fk_model.objects.filter(name__in=user_input.split(","))
        if not selection:
            selection = fk_model.objects.filter(name__in=user_input.split(" "))
        return selection

    def location_as_dict(self):
        loc_dict = {}
        if self.location_desc:
            loc_model = self._meta.get_field("location_key").related_model
            locations = self.select_location_by_input(self.location_desc, loc_model)
            loc_dict.update(
                location_selection=locations,
                location=self.location_desc,
            )
        if self.location_key:
            region_name = self.location_key.region.name.replace(" ", "_").replace(
                "-", "_"
            )
            loc_dict.update(region=region_name)

        return loc_dict

    def _get_location_choices_as_buttons(self, select_field):
        selection = self.data_as_dict().get(select_field)
        row_len = 1
        names = [
            dict(text=f"{entry.name} (регион: {entry.region.name})")
            for entry in selection
        ]
        buttons = [
            names[i : i + row_len] for i in range(0, len(names), row_len)  # noqa E203
        ]
        return buttons

    def _add_location_choices(self, msg):
        field_name = msg.get("confirm_choices")
        if field_name:
            buttons_as_list = self._get_location_choices_as_buttons(field_name)
            buttons_as_list.extend(msg.get("text_buttons"))
            msg["text_buttons"] = buttons_as_list

        return msg


class CacheableFillDataModel(models.Model):
    """
    Компонент для подготовки данных под заполнение шаблонов ответов
    и реализации их кеширования.
    """

    strings_container = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_dict = dict()
        self.data_as_dict()

    def set_dict_data(self, **kwargs):
        for key, value in kwargs.items():
            self._data_dict[key] = value

    # todo separate into a manager?
    def data_as_dict(self):
        """
        Возвращает данные, релевантные для формирования ответов пользователям,
        в виде словаря.
        """

        data_dict = self._data_dict
        if not data_dict:
            post = None
            if self.is_complete:
                post = self.registered
                registered_pk = post.pk
            else:
                registered_pk = "000"
            data_dict = dict(
                channel_name=self.get_tg_instance().publish_name,  #
                request_pk=self.pk,  #
                car_type=self.car_type,  #
                desc=self.description,  #
                user_pk=self.user.pk,  #
                user_name=self.user.name,  #
                user_phone=self.user.phone,  #
                user_tg_id=self.user.user_id,  #
                post_object=post,
                registered_pk=registered_pk,  #
            )
        return data_dict

    def _fill_data(self, message_data: dict) -> dict:
        """Подставляет нужные данные в тело ответа и параметры кнопок."""

        msg = copy.deepcopy(message_data)
        if msg.get("text"):
            msg["text"] = msg["text"].format(**self.data_as_dict())
        m2m_field_name = msg.get("attr_choices")
        button_type = "buttons" if msg.get("buttons") else "text_buttons"
        if m2m_field_name:
            buttons_as_list = self._get_m2m_choices_as_buttons(m2m_field_name)
            buttons_as_list.extend(msg.get(button_type))
            msg[button_type] = buttons_as_list
        if keyboard := msg.get(button_type):
            for row in keyboard:
                for button in row:
                    for field in button.keys():
                        button[field] = button[field].format(**self.data_as_dict())

        return msg

    def _get_m2m_choices_as_buttons(self, field_name):
        m2m_model = self._meta.get_field(field_name).related_model
        field = getattr(self, field_name)
        button_flags = [
            (tag.name, tag in field.all()) for tag in m2m_model.objects.all()
        ]
        row_len = 2
        names = [
            dict(
                text=f"{'☑' if entry[1] else '☐'} {entry[0]}",
                callback_data=f"button {num}",
            )
            for num, entry in enumerate(button_flags)
        ]
        buttons = [
            names[i : i + row_len] for i in range(0, len(names), row_len)  # noqa: E203
        ]
        return buttons


class DialogProcessableEntity(models.Model):

    dialog = None
    stage = None

    class Meta:
        abstract = True

    def get_reply_for_stage(self) -> dict:
        pass

    def is_done(self) -> bool:
        pass

    def check_data(self) -> bool:
        pass

    def invoice_requested(self) -> bool:
        pass
