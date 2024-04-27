import customtkinter as ctk
import tkinter as tk
from PIL import Image
from tkinter.filedialog import askopenfilename, asksaveasfilename
import binascii
import threading
import serial.tools.list_ports
import serial
import time


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class message_window(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x200")
        self.title("Message")

        self.message_label = ctk.CTkLabel(
            self, text="messge", font=("Montserrat", 16), padx=10, pady=10
        )
        self.message_label.place(x=150, y=75)

        self.close_button = ctk.CTkButton(self, text="OK", command=self.on_close)
        self.close_button.place(x=170, y=150)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.destroy()
        app.message_window = None


def open_file(window, text_box):
    filepath = askopenfilename(
        filetypes=[("ROM Files", "*.CAP"), ("BIN Files", "*.bin")]
    )
    if not filepath:
        app.message_window.config(text="No file is selected")
        return

    text_box.delete(1.0, tk.END)

    def read_file_chunk(file, chunk_size):
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            hex_content = binascii.hexlify(chunk).decode("utf-8")
            formatted_hex_content = " ".join(
                hex_content[i : i + 2] for i in range(0, len(hex_content), 2)
            )
            text_box.insert(tk.END, formatted_hex_content + "\n")

    with open(filepath, "rb") as f:
        chunk_size = 4096
        thread = threading.Thread(target=read_file_chunk, args=(f, chunk_size))
        thread.start()


def save_file():
    pass


class CustomUSBPortCombobox(ctk.CTkComboBox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.usb_ports = self.list_uart_ports()
        self.update_usb_ports()

    def list_uart_ports(self):
        ports = serial.tools.list_ports.comports()
        return [device.device for device in ports]

    def update_usb_ports(self):
        self._items = tuple(self.usb_ports)
        if self.usb_ports:
            self.set(self.usb_ports[0])
        else:
            self.set("No devices")

    def refresh_ports(self):
        self.usb_ports = self.list_uart_ports()
        self.update_usb_ports()


class ChipInfo:
    def __init__(self, name, id, mem_size, no_pages, no_bytes, no_blocks):
        self.name = name
        self.identifier = id
        self.mem_size = mem_size
        self.no_pages = no_pages
        self.no_bytes = no_bytes
        self.no_blocks = no_blocks


chip_collections = [
    ChipInfo("W25Q80", 4014, 1048576, 4096, 256, 16),
    ChipInfo("W25Q16", 4015, 2097152, 8192, 512, 32),
    ChipInfo("W25Q32", 4016, 4194304, 16384, 1024, 64),
    ChipInfo("W25Q64", 4017, 8388608, 32768, 2048, 128),
    ChipInfo("W25Q128", 4018, 16777216, 65536, 4096, 256),
]


def push_error(message):
    error_window = None
    if error_window is None or error_window.winfo_exists():
        error_window = message_window()
    else:
        error_window.deiconify()
        error_window.focus()
    error_window.message_label.configure(text=message, text_color="red")


def read(usb_port, current_chip_model, text_box):
    current_usb_port = usb_port
    if current_chip_model is None or current_usb_port == "No devices":
        push_error("No ports are selected")
    else:
        serial_device = serial.Serial(port=current_usb_port, baudrate=115200)
    for models in chip_collections:
        if models.name == current_chip_model:
            no_of_pages = models.no_pages
    text_box.delete(1.0, tk.END)
    for i in range(no_of_pages):
        while serial_device.read() != "W":
            continue
        serial_device.write("G")

        for j in range(256):
            byte = serial_device.read()
            formatted_content = " ".join(
                byte[i : i + 2] for i in range(0, len(byte), 2)
            )
            text_box.insert(tk.END, formatted_content + "\n")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BIOS Programmer")
        self.geometry("1100x580")
        self.resizable(False, False)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidemenu = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidemenu.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidemenu.grid_rowconfigure(4, weight=0)

        self.sidemenu_label = ctk.CTkLabel(
            self,
            text="CHIP INFO",
            font=("Montserrat", 16),
            padx=10,
            pady=10,
            bg_color="blue",
            width=250,
        )
        self.sidemenu_label.grid(row=0, column=0)
        self.sidemenu_label.place(x=0, y=0)

        self.topmenu = ctk.CTkFrame(
            self,
            width=850,
            corner_radius=0,
        )
        self.topmenu.grid(
            row=0, column=1, columnspan=3, rowspan=4, padx=10, sticky="nsew"
        )
        self.topmenu.grid_columnconfigure(0, weight=1)

        open_image = ctk.CTkImage(
            light_image=Image.open("App/open.png"),
            dark_image=Image.open("App/open.png"),
            size=(50, 50),
        )
        self.open_button = ctk.CTkButton(
            self.topmenu,
            text="OPEN",
            font=("Montserrat", 16),
            corner_radius=12,
            width=70,
            height=70,
            image=open_image,
            fg_color="transparent",
            compound=tk.TOP,
            command=lambda: open_file(self, self.text_box),
        )
        self.open_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.open_button.place(x=25, y=25)

        save_image = ctk.CTkImage(
            light_image=Image.open("App/save.png"),
            dark_image=Image.open("App/save.png"),
            size=(50, 50),
        )
        self.save_button = ctk.CTkButton(
            self.topmenu,
            text="SAVE",
            font=("Montserrat", 16),
            corner_radius=12,
            width=70,
            height=70,
            image=save_image,
            fg_color="transparent",
            compound=tk.TOP,
        )
        self.save_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.save_button.place(x=125, y=25)

        read_image = ctk.CTkImage(
            light_image=Image.open("App/read.png"),
            dark_image=Image.open("App/read.png"),
            size=(50, 50),
        )
        self.read_button = ctk.CTkButton(
            self.topmenu,
            text="READ",
            font=("Montserrat", 16),
            corner_radius=12,
            width=70,
            height=70,
            image=read_image,
            fg_color="transparent",
            compound=tk.TOP,
            command=lambda: read(
                self.usb_ports_combobox.get(),
                self.chip_info_combobox.get(),
                self.text_box,
            ),
        )
        self.read_button.grid(row=0, column=1, padx=10, pady=10, stick="nsew")
        self.read_button.place(x=225, y=25)

        write_image = ctk.CTkImage(
            light_image=Image.open("App/write.png"),
            dark_image=Image.open("App/write.png"),
            size=(50, 50),
        )
        self.write_button = ctk.CTkButton(
            self.topmenu,
            text="WRITE",
            font=("Montserrat", 16),
            corner_radius=12,
            width=70,
            height=70,
            image=write_image,
            fg_color="transparent",
            compound=tk.TOP,
        )
        self.write_button.grid(row=0, column=1, padx=10, pady=10, stick="nsew")
        self.write_button.place(x=325, y=25)

        erase_image = ctk.CTkImage(
            light_image=Image.open("App/erase.png"),
            dark_image=Image.open("App/erase.png"),
            size=(50, 50),
        )
        self.erase_button = ctk.CTkButton(
            self.topmenu,
            text="ERASE",
            font=("Montserrat", 16),
            corner_radius=12,
            width=70,
            height=70,
            image=erase_image,
            fg_color="transparent",
            compound=tk.TOP,
        )
        self.erase_button.grid(row=0, column=1, padx=10, pady=10, stick="nsew")
        self.erase_button.place(x=425, y=25)

        self.text_box = ctk.CTkTextbox(self.topmenu, width=850, height=450)
        self.text_box.grid(
            row=0, column=1, columnspan=5, padx=10, pady=10, sticky="nsew"
        )
        self.text_box.place(x=0, y=120)

        self.usb_ports_combobox = CustomUSBPortCombobox(self.topmenu)
        self.usb_ports_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.usb_ports_combobox.place(x=525, y=45)

        self.refresh_button = ctk.CTkButton(
            self,
            text="🗘",
            command=self.usb_ports_combobox.refresh_ports,
            fg_color="transparent",
            width=20,
            corner_radius=10,
        )
        self.refresh_button.place(x=935, y=45)

        self.chip_info_combobox = ctk.CTkComboBox(
            self.sidemenu,
            height=10,
            width=150,
            justify="left",
            command=self.refresh_chiP_info,
        )
        self.chip_info_combobox.grid(row=0, column=0, padx=10, sticky="nsew")
        self.chip_info_combobox.place(x=50, y=50)
        self.chip_info_combobox.set("Select Chip")

        chip_names = [chip_info.name for chip_info in chip_collections]
        self.chip_info_combobox.configure(values=chip_names)

        self.chip_info_label = ctk.CTkLabel(
            self.sidemenu,
            text="Model :"
            + self.chip_info_combobox.get()
            + "\n"
            + "ID         : "
            + "\n"
            + "Size      : "
            + "\n",
            width=250,
            justify="left",
            pady=25,
            padx=25,
            font=("Montserrat", 16),
            text_color="white",
            bg_color="blue",
        )
        self.chip_info_label.grid(row=1, column=0, padx=10, sticky="nsew")
        self.chip_info_label.place(x=0, y=120)

    def refresh_chiP_info(self, choice):
        for chip_data in chip_collections:
            if chip_data.name == choice:
                id = chip_data.identifier
                size = chip_data.mem_size / 1024
        self.chip_info_label.configure(
            text="Model : "
            + choice
            + "\n"
            + "ID         : "
            + str(id)
            + "\n"
            + "Size      : "
            + str(size)
            + "MB"
            + "\n"
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()
