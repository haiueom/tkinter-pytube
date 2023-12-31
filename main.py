import os
import tkinter
import customtkinter
import threading
from pytube import YouTube, exceptions as pyte
from datetime import datetime
from urllib import error as ule

customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("system")
start_time = datetime.now()


def main():
    def show_message(type="", text=""):
        """Show a message on message_label"""
        if type == "error":
            message_label.configure(text=text, text_color="red")
        elif type == "success":
            message_label.configure(text=text, text_color="green")
        elif type == "proccess":
            message_label.configure(text=text, text_color="blue")
        else:
            message_label.configure(text=text)

    def show_popup(type: str, title: str, text: str):
        """Show a windows pop up notification."""
        if type == "info":
            tkinter.messagebox.showinfo(title, text)
        elif type == "error":
            tkinter.messagebox.showerror(title, text)

    def set_out_dir():
        """Open select directory from explorer and set out_dir_var."""
        directory = customtkinter.filedialog.askdirectory(
            initialdir=out_dir_var.get(),
            title="Select a Folder",
            mustexist=True,
        )
        if directory == "":
            directory = out_dir_var.get()
            return
        out_dir_label.configure(text=f"Output: {directory}")
        out_dir_var.set(directory)

    def download_task(event=None):
        """Download the video from the provided url"""
        set_widget_state("disabled")
        show_message("proccess", "Processing...")
        url = url_var.get()
        res = resolution_var.get()
        if url == "":
            show_message("error", "URL is empty")
            set_widget_state("normal")
            return
        try:
            yt = YouTube(url=url)
            list_res = [
                stream.resolution for stream in yt.streams.filter(progressive=True)
            ]
            yt.register_on_progress_callback(on_progress)
            video = yt.streams.filter(res=res, file_extension="mp4").first()
            if video is None:
                show_message(
                    "error",
                    f"ERROR: Video dengan resolution {res} tidak tersedia. resolution yang tersedia adalah {list_res}",
                )
                set_widget_state("normal")
                return
            set_video_info(video.title, video.resolution, video.filesize_mb)
            video.download(out_dir_var.get())
        except (ule.URLError, ule.HTTPError):
            show_message("error", "ERROR: No internet connection.")
            show_popup("error", "Connection Error", "ERROR: No internet connection.")
            set_widget_state("normal")
            return
        except pyte.RegexMatchError:
            show_message("error", "Invalid Youtube Link")
            set_widget_state("normal")
            return
        except Exception as e:
            show_message("error", f"ERROR")
            show_popup("error", "Error", f"{e}")
            set_widget_state("normal")
            return
        show_message("success", "Download Completed")
        show_popup(
            "info",
            "Download Completed",
            f"Judul: {video.title}\nresolution: {res}\nvideo_size_label: {video.filesize_mb:.2f} MB\nOutput: {out_dir_var.get()}",
        )
        set_widget_state("normal")

    def on_progress(stream, chunk, bytes_remaining):
        """Update the progress and speed values in the treeview list"""
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100

        elapsed_time = (datetime.now() - start_time).total_seconds()
        download_speed = bytes_downloaded / (1024 * elapsed_time)

        show_message(
            "proccess",
            f"Downloading {count_file_size(bytes_downloaded)} MB of {count_file_size(total_size)} MB ({percentage:.2f}%) at {download_speed < 1024 and f'{download_speed:.2f} KB/s' or f'{download_speed / 1024:.2f} MB/s'}",
        )

    def on_url_entry_right_click(event):
        """Handle right click on url_entry"""
        try:
            url_entry_right_click_menu.post(event.x_root, event.y_root)
        finally:
            url_entry_right_click_menu.grab_release()

    def paste_url():
        """Handle the 'Paste' option for the url_entry"""
        clipboard_text = app.clipboard_get()
        url_entry.insert("end", clipboard_text)

    def delete_url():
        """Handle the 'Delete' option for the url_entry"""
        url_entry.delete(0, "end")

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
        return round(size_bytes / (1024 * 1024), 2)

    def download():
        """Start a download_task"""
        threading.Thread(target=download_task).start()

    def set_widget_state(state):
        """Set the widget state"""
        download_button.configure(state=state)
        url_entry.configure(state=state)
        resolution_opt_menu.configure(state=state)
        if state == "disabled":
            out_dir_label.unbind("<Button-1>")
        elif state == "normal":
            out_dir_label.bind("<Button-1>", lambda event: set_out_dir())

    def set_video_info(title="", res="", size=""):
        """Set the video_title_label and video_size_label"""
        video_title_label.configure(text=title)
        video_size_label.configure(text=f"{res} | {size:.2f} MB")

    # App Main Window
    app = customtkinter.CTk()
    app.title("Youtube Downloader")
    center_window(app, 400, 330)
    app.resizable(False, False)

    # Title Label
    title_label = customtkinter.CTkLabel(
        app, text="Insert a YouTube link", font=("Arial", 20)
    )
    title_label.pack(padx=10, pady=20)

    # Url Input Entry
    url_var = customtkinter.StringVar()
    url_entry = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_var)
    url_entry.pack(padx=10, pady=0)
    url_entry.focus()
    url_entry_right_click_menu = tkinter.Menu(url_entry, tearoff=0)
    url_entry_right_click_menu.add_command(label="Paste", command=paste_url)
    url_entry_right_click_menu.add_command(label="Delete", command=delete_url)
    url_entry.bind("<Button-3>", on_url_entry_right_click)
    url_entry.bind("<Return>", lambda event: download())
    url_entry.bind("<Control-z>", lambda event: delete_url())

    # Menssage Label
    message_label = customtkinter.CTkLabel(app, wraplength=200, text="")
    message_label.pack(padx=10, pady=10)

    # Video Tittle Label
    video_title_label = customtkinter.CTkLabel(app, text="", wraplength=300)
    video_title_label.pack(padx=10, pady=(0, 2))

    # Video Size Label
    video_size_label = customtkinter.CTkLabel(app, text="")
    video_size_label.pack(padx=10, pady=(0, 2))

    # Output Directory Label
    out_dir_var = customtkinter.StringVar(value=f"{os.path.expanduser('~')}\\Downloads")
    out_dir_label = customtkinter.CTkLabel(
        app, text=f"Output: {out_dir_var.get()}", wraplength=300
    )
    out_dir_label.pack(padx=10, pady=(0, 2))
    out_dir_label.bind("<Button-1>", lambda event: set_out_dir())

    # Frame Container
    frame1 = customtkinter.CTkFrame(app, fg_color="transparent")
    frame1.pack(padx=10, pady=(0, 20))

    # Resolution Option Menu
    resolution_var = customtkinter.StringVar(value="720p")
    resolution_opt_menu = customtkinter.CTkOptionMenu(
        frame1, values=["720p", "480p", "360p", "240p", "144p"], variable=resolution_var
    )
    resolution_opt_menu.grid(row=0, column=0, pady=20, padx=20, sticky="ew")

    # Download Button
    download_button = customtkinter.CTkButton(frame1, text="Download", command=download)
    download_button.grid(row=0, column=1, pady=20, padx=20, sticky="ew")

    # Run App
    app.mainloop()


if __name__ == "__main__":
    main()
