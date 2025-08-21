def checkInvalidFileName(str):
    if len(str) == 0:
        return False

    num = list("1234567890")
    word = list("abcdefghijklmnopqrstuvwxyz" + "abcdefghijklmnopqrstuvwxyz".upper())
    mark = list("_-.")
    check_set = num + word + mark

    for c in list(str):
        if c not in check_set:
            return False

    return True
