import os
import sys
import pandas as pd
from tkinter import Tk, Label, Entry, Button, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk

# ------------------------------
# Dynamic resource resolver
# ------------------------------
def resource_path(relative_path):
    """
    When running as EXE using PyInstaller, resources get packaged into _MEIPASS.
    This ensures paths work both frozen (.exe) and normal script mode.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path


CSV_PATH = resource_path("data.csv")
TEMPLATE_PATH = resource_path("badge_template.jpg")
FONT_PATH = resource_path("fonts/Roboto-VariableFont.ttf")
OUTPUT_DIR = "badges_out"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load CSV
df = pd.read_csv(CSV_PATH)


# ------------------------------
# Text helper
# ------------------------------
def draw_centered_text(draw, text, x, y, font, fill=(0, 0, 0)):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pos = (x - tw // 2, y - th // 2)

    # soft shadow
    draw.text((pos[0] + 3, pos[1] + 3), text, font=font, fill=(255, 255, 255, 180))
    draw.text(pos, text, font=font, fill=fill)


# ------------------------------
# Badge generator
# ------------------------------
def generate_badge_image(code):
    row = df[df["Code"] == code]
    if row.empty:
        raise ValueError("Code not found")

    name = str(row.iloc[0]["Name"])
    company = str(row.iloc[0]["Company"])

    img = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # BIG FONT SIZES (better for printing)
    name_size = int(H * 0.30)      # 30% of height
    company_size = int(H * 0.17)   # 17% of height

    try:
        font_name = ImageFont.truetype(FONT_PATH, name_size)
        font_company = ImageFont.truetype(FONT_PATH, company_size)
    except:
        font_name = ImageFont.load_default()
        font_company = ImageFont.load_default()

    # Center positions
    name_x = W // 2
    name_y = int(H * 0.42)

    company_x = W // 2
    company_y = int(H * 0.63)

    draw_centered_text(draw, name, name_x, name_y, font_name)
    draw_centered_text(draw, company, company_x, company_y, font_company)

    return img


# ------------------------------
# GUI
# ------------------------------
root = Tk()
root.title("Badge Printer")

Label(root, text="Enter Code:").grid(row=0, column=0, padx=8, pady=8)
entry = Entry(root)
entry.grid(row=0, column=1, padx=8, pady=8)

preview_label = Label(root)
preview_label.grid(row=2, column=0, columnspan=2, padx=8, pady=8)


def on_preview():
    code = entry.get().strip()
    if not code:
        messagebox.showinfo("Error", "Enter a code")
        return

    try:
        img = generate_badge_image(code)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    # Show preview
    preview = img.copy()
    preview.thumbnail((400, 400))
    tkimg = ImageTk.PhotoImage(preview)
    preview_label.configure(image=tkimg)
    preview_label.image = tkimg

    # Save
    out_path = os.path.join(OUTPUT_DIR, f"badge_{code}.png")
    img.save(out_path)
    messagebox.showinfo("Saved", f"Badge saved to {out_path}")


def on_print():
    code = entry.get().strip()
    if not code:
        messagebox.showinfo("Error", "Enter a code")
        return

    out_path = os.path.join(OUTPUT_DIR, f"badge_{code}.png")

    if not os.path.exists(out_path):
        try:
            img = generate_badge_image(code)
            img.save(out_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

    # Windows — silent print
    if sys.platform.startswith("win"):
        try:
            os.startfile(out_path, "print")
        except Exception as e:
            messagebox.showerror("Print Error", str(e))
    else:
        # Mac / Linux
        try:
            os.system(f"lpr '{out_path}'")
            messagebox.showinfo("Printing", "Sent to printer.")
        except:
            messagebox.showinfo("Printed", "Saved. Print manually.")


Button(root, text="Preview & Save", command=on_preview).grid(row=1, column=0, padx=8, pady=8)
Button(root, text="Print", command=on_print).grid(row=1, column=1, padx=8, pady=8)

root.mainloop()
