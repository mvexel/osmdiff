def join_url(*tuple):
    temp = ""
    for i in tuple:
        temp = temp + '/' + i
    temp = temp[1:]
    return temp