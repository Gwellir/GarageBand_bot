class SingletonByUserID(type):
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            user_id = args[0].id
        else:
            return

        if user_id in cls.__instance:
            return cls.__instance[user_id]
        else:
            cls.__instance[user_id] = super().__call__(*args, **kwargs)
            return cls.__instance[user_id]
