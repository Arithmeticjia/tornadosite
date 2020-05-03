import base64


def get_basic_auth_str(username, password):
    temp_str = username + ':' + password
    # 转成bytes string
    bytesString = temp_str.encode(encoding="utf-8")
    print(bytesString)
    # base64 编码
    encodestr = base64.b64encode(bytesString)
    # 解码

    decodestr = base64.b64decode(encodestr)
    print(decodestr)

    return 'Basic ' + encodestr.decode()


print(get_basic_auth_str("admin", "123"))
