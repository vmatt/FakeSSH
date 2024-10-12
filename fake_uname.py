def uname_handle(cmd):
    if cmd == "uname" or cmd == "uname -s":
        return "Linux"
    elif cmd == "uname -n":
        return "aws-server"
    elif cmd == "uname -r":
        return "5.15.0-83-generic"
    elif cmd == "uname -v":
        return "#92-Ubuntu SMP Wed Oct 4 15:35:50 UTC 2023"
    elif cmd == "uname -m":
        return "x86_64"
    elif cmd == "uname -p":
        return "unknown"
    elif cmd == "uname -i":
        return "unknown"
    elif cmd == "uname -o":
        return "GNU/Linux"
    elif cmd == "uname -a":
        return "Linux aws-server 5.15.0-83-generic #92-Ubuntu SMP Wed Oct 4 15:35:50 UTC 2023 x86_64 GNU/LINUX"
    else:
        return f"command `{cmd}` not found."
