import tkinter as tk
from tkinter import messagebox
import os

# Define the name of the file where the note will be saved.
NOTES_FILE = "my_note.txt"

class NoteApp:
    """A simple GUI application for taking and saving a single note."""

    def __init__(self, root):
        """Initializes the main application window and its widgets."""
        # The 'root' is the main window of the application.
        self.root = root
        self.root.title("Simple Note Taker")
        # Set a minimum size for the window.
        self.root.geometry("600x400")
        
        # Configure a modern font style.
        font_style = ("Segoe UI", 12)

        # Create a title label for the application.
        title_label = tk.Label(root, text="Your Note", font=("Segoe UI", 16, "bold"), pady=10)
        title_label.pack()

        # Create a Text widget for writing the note.
        # This widget allows for multi-line text input.
        self.note_text = tk.Text(root, wrap="word", font=font_style, padx=5, pady=5, relief="flat", bd=1,
                                 bg="#3d3d3d", fg="#EAEAEA",height=10,width=10)
        self.note_text.pack(expand=True, fill="both")

        # Create a frame to hold the buttons at the bottom.
        button_frame = tk.Frame(root, pady=10)
        button_frame.pack()

        # Create the "Save Note" button.
        save_button = tk.Button(button_frame, text="Save Note", font=font_style, command=self.save_note,
                                bg="#7BA07C", fg="white", activebackground="#255427", relief="raised")
        save_button.pack(side="left", padx=5)

        # Create the "Clear Note" button.
        clear_button = tk.Button(button_frame, text="Clear Note", font=font_style, command=self.clear_note,
                                 bg="#fba29c", fg="white", activebackground="#6d0700", relief="raised")
        clear_button.pack(side="left", padx=5)

        # Load any existing note when the app starts.
        self.load_note()

    def load_note(self):
        """Loads the note from the file and displays it in the text widget."""
        # Check if the notes file exists.
        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, 'a+', encoding='utf-8') as f:
                    note_content = f.read()
                    # Delete any existing content in the Text widget before inserting the new content.
                    self.note_text.delete(1.0, tk.END)
                    # Insert the content read from the file.
                    self.note_text.insert(tk.END, note_content)
            except Exception as e:
                # Handle potential errors, e.g., file permission issues.
                messagebox.showerror("Error", f"Failed to load note: {e}")

    def save_note(self):
        """Saves the content of the text widget to the notes file."""
        # Get all text from the widget, from the beginning (1.0) to the end (tk.END).
        note_content = self.note_text.get(1.0, tk.END).strip()
        try:
            with open(NOTES_FILE, 'w', encoding='utf-8') as f:
                # Write the content to the file, overwriting the old content.
                f.write(note_content)
            # Display a success message to the user.
            messagebox.showinfo("Success", "Note saved successfully!")
        except Exception as e:
            # Display an error message if saving fails.
            messagebox.showerror("Error", f"Failed to save note: {e}")

    def clear_note(self):
        """Clears the content of the text widget."""
        # Check if the text widget is not empty before clearing.
        if self.note_text.get(1.0, tk.END).strip():
            # The 'askyesno' function provides a confirmation dialog.
            if messagebox.askyesno("Clear Note", "Are you sure you want to clear the current note?"):
                # Delete all content from the beginning to the end.
                self.note_text.delete(1.0, tk.END)

# This is the standard entry point for a Tkinter application.
# It creates the main window and runs the application.
if __name__ == "__main__":
    # Create the main window instance.
    root = tk.Tk()
    # Create an instance of our NoteApp class, passing the main window to it.
    app = NoteApp(root)
    # Start the Tkinter event loop, which listens for user interactions.
    root.mainloop()