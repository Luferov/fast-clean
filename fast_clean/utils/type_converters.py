"""
Модуль, содержащий функции для преобразования типов.
"""

true_set = {'yes', 'true', 't', 'y', '1'}
false_set = {'no', 'false', 'f', 'n', '0'}


def str_to_bool(value: str) -> bool:
    """
    Преобразуем строку к логическом значению.
    """
    value = value.lower()
    if value in true_set:
        return True
    if value in false_set:
        return False
    raise ValueError('Expected "%s"' % '", "'.join(true_set | false_set))
