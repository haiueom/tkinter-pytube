import tkinter
import customtkinter
import pytube.exceptions
import urllib.error
from pytube import YouTube
from datetime import datetime

customtkinter.set_default_color_theme("blue")
download_start_time = datetime.now()


def main():
    def message(text="", type=""):
        if type == "error":
            msg.configure(text=text, text_color="red")
        elif type == "success":
            msg.configure(text=text, text_color="green")
        elif type == "proccess":
            msg.configure(text=text, text_color="blue")
        else:
            msg.configure(text=text)
        msg.after(3000, lambda: msg.configure(text=""))

    def download(event=None):
        url = urlVar.get()
        res = resVar.get()
        if url == "":
            message("URL is empty", "error")
            return
        yt = YouTube(url=url)
        list_res = [stream.resolution for stream in yt.streams.filter(progressive=True)]
        yt.register_on_progress_callback(progress)
        # set the resolution filter
        video = yt.streams.filter(res=res, file_extension="mp4").first()
        if video is None:
            message(
                f"ERROR: Video dengan resolusi {res} tidak tersedia. Resolusi yang tersedia adalah {list_res}",
                "error",
            )
            return
        try:
            video.download()
        except (urllib.error.URLError, urllib.error.HTTPError):
            message("ERROR: No internet connection.", "error")
            return
        except pytube.exceptions.RegexMatchError:
            message("ERROR: Invalid URL", "error")
            return
        except Exception as e:
            message(f"ERROR", "error")
            tkinter.messagebox.showerror("Error", f"{e}")
            return
        message("Download Completed", "success")
        tkinter.messagebox.showinfo(
            "Download Completed",
            "Judul: {}\nResolusi: {}\nUkuran: {:.2f} MB".format(
                video.title, res, video.filesize_mb
            ),
        )

    def progress(stream, chunk, bytes_remaining):
        """Update the progress and speed values in the treeview list"""
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100

        elapsed_time = (datetime.now() - download_start_time).total_seconds()
        download_speed = bytes_downloaded / (1024 * elapsed_time)

        vitle.configure(text=stream.title)
        ukuran.configure(
            text=f"{stream.resolution} | {count_file_size(stream.filesize)} MB"
        )
        message(
            f"Downloading {count_file_size(bytes_downloaded)} MB of {count_file_size(total_size)} MB ({percentage:.2f}%) at {download_speed < 1024 and f'{download_speed:.2f} KB/s' or f'{download_speed / 1024:.2f} MB/s'}",
            "proccess",
        )

    # Menu functions
    def on_url_entry_right_click(event):
        try:
            url_entry_right_click_menu.post(event.x_root, event.y_root)
        finally:
            url_entry_right_click_menu.grab_release()

    def paste_url():
        """Handle the 'Paste' option for the url_entry"""
        clipboard_text = app.clipboard_get()
        entry.insert("end", clipboard_text)

    def delete_url():
        """Handle the 'Delete' option for the url_entry"""
        entry.delete(0, "end")

    def center_window(window, width, height):
        """Center a window on the screen using the provided dimensions"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")
        window.update_idletasks()

    def count_file_size(size_bytes):
        """Convert bytes to megabytes (MB) for representing file sizes"""
        return round(size_bytes / (1024 * 1024), 1)

    # App Frame
    app = customtkinter.CTk()
    app.title("Youtube Downloader")
    center_window(app, 400, 300)
    app.resizable(False, False)

    # judul
    title = customtkinter.CTkLabel(
        app, text="Insert a YouTube link", font=("Arial", 20)
    )
    title.pack(padx=10, pady=20)

    # text input
    urlVar = customtkinter.StringVar()
    entry = customtkinter.CTkEntry(app, width=350, height=40, textvariable=urlVar)
    entry.pack(padx=10, pady=0)
    entry.focus()

    # right click menu
    url_entry_right_click_menu = tkinter.Menu(entry, tearoff=0)
    url_entry_right_click_menu.add_command(label="Paste", command=paste_url)
    url_entry_right_click_menu.add_command(label="Delete", command=delete_url)
    entry.bind("<Button-3>", on_url_entry_right_click)
    entry.bind("<Return>", download)
    entry.bind("<Control-z>", lambda event: delete_url())

    # pesan
    msg = customtkinter.CTkLabel(app, wraplength=200, text="")
    msg.pack(padx=10, pady=0)

    # judul video
    vitle = customtkinter.CTkLabel(app, text="")
    vitle.pack(padx=10, pady=2)

    # ukuran video
    ukuran = customtkinter.CTkLabel(app, text="")
    ukuran.pack(padx=10, pady=(0, 2))

    # frame 1
    frame1 = customtkinter.CTkFrame(app, fg_color="transparent")
    frame1.pack(padx=10, pady=(0, 20))

    # resolusi
    resVar = customtkinter.StringVar(value="720p")
    resolusi = customtkinter.CTkOptionMenu(
        frame1, values=["720p", "480p", "360p", "240p", "144p"], variable=resVar
    )
    resolusi.grid(row=0, column=0, pady=20, padx=20, sticky="ew")

    # tombol download
    button = customtkinter.CTkButton(frame1, text="Download", command=download)
    button.grid(row=0, column=1, pady=20, padx=20, sticky="ew")

    # Run App
    app.mainloop()


if __name__ == "__main__":
    main()
