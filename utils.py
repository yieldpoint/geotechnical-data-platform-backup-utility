def str_to_bool(str):
    str = str.lower()
    if str in ['1', 'true', 't', 'yes', 'y']:
        return True
    elif str in ['0', 'false', 'f', 'no', 'n']:
        return False
    else:
        raise ValueError("Couldn't convert %s to boolean." % str)
