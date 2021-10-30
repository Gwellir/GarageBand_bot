
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
            telegram_instance=instance
        )


def fill_stages(apps, schema_editor, model_name: str, stages: list):
    app, model = model_name.split(".")
    BFS = apps.get_model(app, model)
    db_alias = schema_editor.connection.alias
    BFS.objects.using(db_alias).bulk_create([
        # name, processor, reply_pattern, buttons
        BFS(**stage) for stage in stages
    ])
