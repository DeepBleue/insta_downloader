import tkinter as tk
from tkinter import ttk, messagebox, StringVar
import instaloader
import os
import glob
import threading
import sys


class InstagramDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Instagram Downloader")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')
        self.geometry('300x300')
        self.set_icon()
        # self.iconbitmap(os.path.abspath('cheeze.ico'))

        # self.iconbitmap('cheeze.ico')
        
        self.stories_tab = StoriesTab(self.notebook)
        self.posts_tab = PostsTab(self.notebook)
        
        self.notebook.add(self.stories_tab, text='Stories')
        self.notebook.add(self.posts_tab, text='Posts')
            

    def set_icon(self):
        # Check if running as a bundled application
        if getattr(sys, 'frozen', False):
            # If so, use the path in _MEIPASS
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_path = os.path.join(application_path, 'cheeze.ico')
        try:
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error setting icon: {e}")

    

class StoriesTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.init_ui()

    def init_ui(self):
        self.username_label = tk.Label(self, text="Username:")
        self.username_label.pack(side='top',pady=(20,0))
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        self.target_profile_label = tk.Label(self, text="Target Profile:")
        self.target_profile_label.pack()
        self.target_profile_entry = tk.Entry(self)
        self.target_profile_entry.pack()

        self.folder_name_label = tk.Label(self, text="Folder Name:")
        self.folder_name_label.pack()

        self.folder_name_var = StringVar()
        self.folder_name_entry = tk.Entry(self, textvariable=self.folder_name_var)
        self.folder_name_entry.pack()
        self.target_profile_entry.bind("<KeyRelease>", lambda event: self.update_folder_name())

        self.download_button = tk.Button(self, text="Download Stories", command=self.on_download_click)
        self.download_button.pack(pady=10)

        self.status_label = tk.Label(self, text="")
        self.status_label.pack()

    def update_folder_name(self, *args):
        folder_name = self.target_profile_entry.get().strip() + "_stories" if self.target_profile_entry.get() else ""
        self.folder_name_var.set(folder_name)

    def on_download_click(self):
        threading.Thread(target=self.download_stories, args=(
            self.username_entry.get(), 
            self.password_entry.get(), 
            self.target_profile_entry.get(), 
            self.folder_name_entry.get(), 
            self.status_label)).start()

    def download_stories(self, username, password, target_profile, folder_name, status_label):
        def update_status(message):
            status_label.config(text=message)

        update_status("Downloading...")
        L = instaloader.Instaloader()
        try:
            L.login(username, password)
        except instaloader.exceptions.LoginError:
            messagebox.showerror("Error", "Login failed. Check your username and password.")
            return
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        try:
            profile = instaloader.Profile.from_username(L.context, target_profile)
            if profile.has_viewable_story:
                L.download_stories(userids=[profile.userid], filename_target=folder_name)
                update_status("Download complete!")
            else:
                update_status(f"{target_profile} does not have any viewable stories.")
        except Exception as e:
            update_status("An error occurred.")
            messagebox.showerror("Error", str(e))

        # Remove .xz files
        download_path = folder_name
        for json_file in glob.glob(os.path.join(download_path, '*.xz')):
            os.remove(json_file)

class PostsTab(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.init_ui()

    def init_ui(self):
        self.url_label = tk.Label(self, text="Post URL:")
        self.url_label.pack(side='top',pady=(20,0))
        self.url_entry = tk.Entry(self)
        self.url_entry.pack()

        self.download_path_label = tk.Label(self, text="Folder name:")
        self.download_path_label.pack()
        self.download_path_entry = tk.Entry(self)
        self.download_path_entry.pack()

        self.download_button = tk.Button(self, text="Download Post", command=self.on_download_click)
        self.download_button.pack(pady=10)

        self.status_label = tk.Label(self, text="")
        self.status_label.pack()

    def on_download_click(self):
        threading.Thread(target=self.download_instagram_post, args=(
            self.url_entry.get(), 
            self.download_path_entry.get(), 
            self.status_label)).start()

    def download_instagram_post(self, url, download_path, status_label):
        def update_status(message):
            status_label.config(text=message)

        update_status("Downloading...")
        L = instaloader.Instaloader(download_videos=True, download_pictures=True, 
                                     download_video_thumbnails=False)
        try:
            shortcode = url.split("/")[-2]  # Extract shortcode from URL
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            # Define filename based on media type
            filename = f"{download_path}/{shortcode}{'_video.mp4' if post.is_video else '_image.jpg'}"
            
            # Download the post
            L.download_post(post, target=download_path)
            
            update_status("Download complete!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            update_status("An error occurred.")
            
        for json_file in glob.glob(os.path.join(download_path, '*.xz')):
            os.remove(json_file)
            
        for text_file in glob.glob(os.path.join(download_path, '*.txt')):
            os.remove(text_file)



# Main application execution
if __name__ == "__main__":
    app = InstagramDownloaderApp()
    app.mainloop()
