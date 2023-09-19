from aiogram.types import Message


def compare_lists(first_list, second_list):
    """Сравниваем списки из аргументов функции и ожидаемыми аргументами.

    Необходимо, т.к. объект Message не сравнивается по обычным полям,
    а делает как то иначе.

    Args:
        first_list:
        second_list:

    Returns:

    """
    if len(first_list) != len(second_list):
        return False

    for i in range(len(first_list)):
        first_argument = first_list[i]
        second_argument = second_list[i]
        if isinstance(first_argument, Message) and isinstance(
            second_argument, Message
        ):
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


def get_attribute_list(mock_func):
    calls = mock_func.call_args_list
    for call in calls:
        args = call[0]
        kwargs = call[1]
        return list(args) + list(kwargs.values())
