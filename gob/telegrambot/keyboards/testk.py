def get_keyboard(
    buttons: list[str],
    row_length=4,
):
    """Create keyboard object by names of buttons.

    Args:
        row_length: Length of every row.
        buttons: Names of needed buttons.

    Returns:
        Keyboard object.

    """
    row = []
    matrix = []
    for index, button in enumerate(buttons):
        row.append(button)
        if (index + 1) % row_length == 0:
            print("1")
            matrix.append(row)
            row = []
    if row:
        matrix.append(row)
    if not matrix and not row:
        return [[]]
    return matrix


lst1 = [1, 2, 3, 4, 5]
lst2 = []
lst3 = [1, 2]
lst4 = [1, 2, 3, 4, 5, 6, 7, 8]

print(
    get_keyboard(
        [
            "Второе",
            "Третье",
            "Больше заведений!",
            "отмена",
        ],
        3,
    )
)
assert get_keyboard([1, 2, 3, 4, 5], 4) == [[1, 2, 3, 4], [5]]
assert get_keyboard([], 4) == [[]]
assert get_keyboard([1, 2]) == [[1, 2]]
assert get_keyboard([1, 2, 3, 4, 5, 6, 7, 8]) == [[1, 2, 3, 4], [5, 6, 7, 8]]
