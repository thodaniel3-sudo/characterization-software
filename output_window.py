# ============================================================
#  OUTPUT DISPLAY WINDOW MODULE  — BULLETPROOF VERSION
# ============================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os


def _is_alive(toplevel):
    """Safely check whether a Toplevel still exists."""
    if toplevel is None:
        return False
    try:
        return bool(toplevel.winfo_exists())
    except tk.TclError:
        return False
    except Exception:
        return False


class OutputWindow:
    _instance = None

    def __init__(self, title="Program Output"):
        # ---- Reuse if alive ----
        if OutputWindow._instance is not None:
            if _is_alive(OutputWindow._instance.window):
                ref = OutputWindow._instance
                self.window = ref.window
                self._image_refs = ref._image_refs
                self.canvas = ref.canvas
                self.images_inner = ref.images_inner
                self.report_text = ref.report_text
                self.analysis_text = ref.analysis_text
                try:
                    self.window.lift()
                    self.window.focus_force()
                except tk.TclError:
                    pass
                return
            else:
                # Dead instance — throw it away
                OutputWindow._instance = None

        OutputWindow._instance = self

        # ---- Create fresh window ----
        self.window = tk.Toplevel()
        self.window.title(title)
        self.window.geometry("980x760")
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        # IMAGES
        self.images_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.images_frame, text="Images")

        self.canvas = tk.Canvas(self.images_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, side="left")
        vbar = ttk.Scrollbar(self.images_frame, orient="vertical",
                             command=self.canvas.yview)
        vbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=vbar.set)

        self.images_inner = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.images_inner, anchor="nw")
        self.images_inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # REPORTS
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Reports")

        self.report_text = tk.Text(
            self.reports_frame, wrap="word", font=("Consolas", 11),
            bg="#1e1e1e", fg="#dcdcdc"
        )
        self.report_text.pack(fill="both", expand=True, side="left")
        rbar = ttk.Scrollbar(self.reports_frame, orient="vertical",
                             command=self.report_text.yview)
        rbar.pack(side="right", fill="y")
        self.report_text.configure(yscrollcommand=rbar.set)

        # ANALYSIS
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Analysis")

        self.analysis_text = tk.Text(
            self.analysis_frame, wrap="word", font=("Consolas", 11),
            bg="#1e1e1e", fg="#7CFC00"
        )
        self.analysis_text.pack(fill="both", expand=True, side="left")
        abar = ttk.Scrollbar(self.analysis_frame, orient="vertical",
                             command=self.analysis_text.yview)
        abar.pack(side="right", fill="y")
        self.analysis_text.configure(yscrollcommand=abar.set)

        # Bottom buttons
        bar = ttk.Frame(self.window)
        bar.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(bar, text="Clear All", command=self.clear_all).pack(side="left")
        ttk.Button(bar, text="Save Report...", command=self.save_report).pack(side="left", padx=6)
        ttk.Button(bar, text="Hide", command=self.window.withdraw).pack(side="right")
        ttk.Button(bar, text="Close", command=self.close).pack(side="right", padx=6)

        self._image_refs = []

    # ---------- Safe display helpers ----------
    def _safe(self, func, *args, **kwargs):
        """Run a method only if the window is alive."""
        if not _is_alive(self.window):
            # Try to rebuild once
            if OutputWindow._instance is not None:
                OutputWindow._instance = None
            return None
        try:
            return func(*args, **kwargs)
        except tk.TclError:
            return None

    def add_image(self, path, max_width=820, caption=None):
        if not _is_alive(self.window):
            return
        try:
            img = Image.open(path)
            w, h = img.size
            if w > max_width:
                ratio = max_width / w
                img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

            tkimg = ImageTk.PhotoImage(img)

            frame = ttk.Frame(self.images_inner)
            frame.pack(padx=10, pady=10, anchor="w")

            lbl = ttk.Label(frame, image=tkimg)
            lbl.image = tkimg
            lbl.pack()
            self._image_refs.append(tkimg)

            label_text = caption if caption else os.path.basename(path)
            ttk.Label(frame, text=label_text, font=("Segoe UI", 9, "italic")).pack()

            self.show()
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load image:\n{e}")

    def add_image_from_array(self, array, caption=None, max_width=820):
        if not _is_alive(self.window):
            return
        try:
            img = array if isinstance(array, Image.Image) else Image.fromarray(array)
            w, h = img.size
            if w > max_width:
                ratio = max_width / w
                img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

            tkimg = ImageTk.PhotoImage(img)
            frame = ttk.Frame(self.images_inner)
            frame.pack(padx=10, pady=10, anchor="w")

            lbl = ttk.Label(frame, image=tkimg)
            lbl.image = tkimg
            lbl.pack()
            self._image_refs.append(tkimg)

            if caption:
                ttk.Label(frame, text=caption,
                          font=("Segoe UI", 9, "italic")).pack()

            self.show()
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not display image:\n{e}")

    def add_report(self, text, append=True):
        if not _is_alive(self.window):
            return
        try:
            if not append:
                self.report_text.delete("1.0", tk.END)
            self.report_text.insert(tk.END, text + "\n")
            self.report_text.see(tk.END)
            self.show()
        except tk.TclError:
            pass

    def add_analysis(self, text, append=True):
        if not _is_alive(self.window):
            return
        try:
            if not append:
                self.analysis_text.delete("1.0", tk.END)
            self.analysis_text.insert(tk.END, text + "\n")
            self.analysis_text.see(tk.END)
            self.show()
        except tk.TclError:
            pass

    def show(self):
        if not _is_alive(self.window):
            return
        try:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
        except tk.TclError:
            pass

    def clear_all(self):
        if not _is_alive(self.window):
            return
        try:
            for widget in self.images_inner.winfo_children():
                widget.destroy()
            self._image_refs.clear()
            self.report_text.delete("1.0", tk.END)
            self.analysis_text.delete("1.0", tk.END)
        except tk.TclError:
            pass

    def save_report(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write("=== REPORT ===\n")
                f.write(self.report_text.get("1.0", tk.END))
                f.write("\n=== ANALYSIS ===\n")
                f.write(self.analysis_text.get("1.0", tk.END))
            messagebox.showinfo("Saved", f"Report saved to:\n{path}")

    def close(self):
        try:
            if _is_alive(self.window):
                self.window.destroy()
        except tk.TclError:
            pass
        OutputWindow._instance = None


# ---------- Convenience wrappers ----------
def _get_or_create():
    """Return a live OutputWindow, rebuilding if the old one is dead."""
    inst = OutputWindow._instance
    if inst is not None and _is_alive(inst.window):
        try:
            inst.show()
            return inst
        except Exception:
            OutputWindow._instance = None
    return OutputWindow()


def show_output(title="Program Output"):
    inst = OutputWindow._instance
    if inst is not None and _is_alive(inst.window):
        inst.show()
        return inst
    return OutputWindow(title)


def output_image(path, caption=None):
    w = _get_or_create()
    w.add_image(path, caption=caption)


def output_image_array(array, caption=None):
    w = _get_or_create()
    w.add_image_from_array(array, caption=caption)


def output_report(text):
    w = _get_or_create()
    w.add_report(text)


def output_analysis(text):
    w = _get_or_create()
    w.add_analysis(text)