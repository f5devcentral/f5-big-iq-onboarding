import string


def valid_master_passphrase(value):
    if value is None:
        return False
    if len(value) < 16:
        return False
    up = sum(1 for c in value if c.isupper())
    if up < 1:
        return False
    down = sum(1 for c in value if c.islower())
    if down < 1:
        return False
    letter = sum(1 for c in value if c.isalpha())
    if letter < 1:
        return False
    number = sum(1 for c in value if c.isdigit())
    if number < 1:
        return False
    special = sum(1 for c in value if c in string.punctuation)
    if special < 1:
        return False
    return True


class FilterModule(object):
    def filters(self):
        return {
            'valid_master_passphrase': valid_master_passphrase
        }
