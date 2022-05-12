from django.db.models import F


def delete_bots(apps, schema_editor, names: list):
    BotTable = apps.get_model("tgbot", "MessengerBot")
    TGITable = apps.get_model("tgbot", "TGInstance")
    db_alias = schema_editor.connection.alias
    instances = TGITable.objects.using(db_alias).filter(bot__name__in=names)
    BotTable.objects.using(db_alias).delete(name__in=names)
    instances.delete()


def add_bots(apps, schema_editor, bots: list):
    """
    :param bots:
    [
        {
            "instance":
            {
                "token": token,
                "publish_id": pub_id,
                "publish_name": str,
                "admin_group_id": admin_id,
            },
            "name": bot name,
            "bound_object": BO name,
            "is_active": ON key,
            "is_debug": debug key,
            "bound_app": bound app name,
        },
        {...}
    ]
    :return:
    """
    BotTable = apps.get_model("tgbot", "MessengerBot")
    TGITable = apps.get_model("tgbot", "TGInstance")
    db_alias = schema_editor.connection.alias
    for msg_bot in bots:
        instance = TGITable.objects.using(db_alias).create(
            # token, publish_id, publish_name, admin_group_id
            **msg_bot.pop("instance")
        )
        BotTable.objects.using(db_alias).create(
            # name, bound_object, is_active, is_debug, bound_app
            **msg_bot,
            telegram_instance=instance,
        )


def fill_rows(apps, schema_editor, model_name: str, rows_data: list):
    app, model = model_name.split(".")
    Model = apps.get_model(app, model)
    db_alias = schema_editor.connection.alias
    Model.objects.using(db_alias).bulk_create(
        [
            # name, processor, reply_pattern, buttons
            Model(**row)
            for row in rows_data
        ]
    )


def add_foreign_keys(
    apps, schema_editor, model_name, key_model_name, keys, relation_name
):
    db_alias = schema_editor.connection.alias
    app, model = model_name.split(".")
    object_model_query = apps.get_model(app, model).objects.using(db_alias)
    app, model = key_model_name.split(".")
    object_key_model_query = apps.get_model(app, model).objects.using(db_alias)
    for key in keys:
        id_ = key.get("id")
        for key_above in object_key_model_query.filter(id__gte=id_).order_by("-id"):
            key_above.id += 1
            key_above.save()
        object_key_model_query.filter(id=id_).delete()
        object_key_model_query.create(**key)
        object_model_query.filter(**{f"{relation_name}_id__gte": id_}).update(
            **{f"{relation_name}_id": F(f"{relation_name}_id") + 1}
        )


def del_foreign_keys(
    apps, schema_editor, model_name, key_model_name, ids, relation_name
):
    db_alias = schema_editor.connection.alias
    app, model = model_name.split(".")
    object_model_query = apps.get_model(app, model).objects.using(db_alias)
    app, model = key_model_name.split(".")
    object_key_model_query = apps.get_model(app, model).objects.using(db_alias)
    last_id = object_key_model_query.count()
    for id_ in ids:
        for key_above in object_key_model_query.filter(id__gte=id_).order_by("-id"):
            key_above.id -= 1
            key_above.save()
        object_key_model_query.filter(id=last_id).delete()
        object_model_query.filter(**{f"{relation_name}_id__gt": id_}).update(
            **{f"{relation_name}_id": F(f"{relation_name}_id") - 1}
        )
