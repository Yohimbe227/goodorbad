from aiogram.types import Message


def compare_lists(first_list, second_list):
    if len(first_list) != len(second_list):
        return False

    for i in range(len(first_list)):
        first_argument = first_list[i]
        second_argument = second_list[i]
        if isinstance(first_argument, Message) and isinstance(second_argument, Message):
            if first_argument.message_id != second_argument.message_id:
                return False
            if first_argument.date != second_argument.date:
                return False
            if first_argument.from_user.id != second_argument.from_user.id:
                return False
            if first_argument.chat.id != second_argument.chat.id:
                return False
        else:
            if first_argument != second_argument:
                return False
    return True


def monkey_patch_message():
    original_init = Message.__init__

    def custom_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.custom_compared_fields = []

    def __eq__(self, other):
        if not isinstance(other, Message):
            return False

        for field in self.custom_compared_fields:
            if getattr(self, field) != getattr(other, field):
                return False

        return True

    Message.__init__ = custom_init
