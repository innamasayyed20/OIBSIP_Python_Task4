import tkinter as tk
from tkinter import ttk, messagebox
import requests
import geocoder
import datetime
from PIL import Image, ImageTk

# --- Constants & Config ---
API_KEY = "0f11d9bc5e16c8705dd4f8812b06bb1f"
FONT_MAIN = "Segoe UI"
PRIMARY = "#3b82f6"  
ACCENT = "#6366f1"   
TEXT_DARK = "#1e293b" 

ICON = {"Clear":"☀","Clouds":"☁","Rain":"🌧","Mist":"🌫","Smoke":"💨",
        "Haze":"🌫","Snow":"❄","Drizzle":"🌦","Thunderstorm":"⛈"}

def create_gradient_bg(width, height, color1, color2):
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

# --- Logic Functions ---
def fetch(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},IN&appid={API_KEY}&units=metric"
    data = requests.get(url).json()
    return data['list'][::8]

def detect():
    try:
        g = geocoder.ip('me')
        if g.city: 
            city_var.set(g.city)
            status_label.config(text=f"📍 Detected: {g.city}", fg=PRIMARY)
    except:
        status_label.config(text="❌ Detection Failed", fg="#ef4444")

def get_weather(event=None):
    city = city_var.get().strip()
    if not city:
        messagebox.showwarning("Warning", "Enter a city name")
        return
    try:
        status_label.config(text="⏳ Loading...", fg=PRIMARY)
        root.update()
        d, f = fetch(city), forecast(city)
        if str(d.get("cod"))=="200":
            status_label.config(text="✅ Ready", fg="#10b981")
            show_weather_popup(d, f)
        else:
            status_label.config(text="❌ City not found", fg="#ef4444")
    except:
        status_label.config(text="❌ Connection Error", fg="#ef4444")

# --- Results UI ---
def show_weather_popup(d, fdata):
    win = tk.Toplevel(root)
    win.title(f"SkyCast - {d['name']}")
    win.state("zoomed")
    
    W, H = win.winfo_screenwidth(), win.winfo_screenheight()
    grad = create_gradient_bg(W, H, (240, 244, 248), (200, 220, 240))
    bg_img = ImageTk.PhotoImage(grad)
    lbl = tk.Label(win, image=bg_img); lbl.image = bg_img; lbl.place(x=0, y=0)

    canvas = tk.Canvas(win, bg="#f0f4f8", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    
    scroll_frame = tk.Frame(canvas, bg="#f0f4f8")
    canvas.create_window((W//2, 0), window=scroll_frame, anchor="n")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        if event.num == 4 or event.delta > 0: canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0: canvas.yview_scroll(1, "units")
            
    win.bind_all("<MouseWheel>", _on_mousewheel)
    win.bind_all("<Button-4>", _on_mousewheel)
    win.bind_all("<Button-5>", _on_mousewheel)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    tk.Label(scroll_frame, text=d['name'].upper(), font=(FONT_MAIN, 40, "bold"), fg=TEXT_DARK, bg="#f0f4f8").pack(pady=(40,5))
    tk.Label(scroll_frame, text=datetime.datetime.now().strftime("%A, %d %B"), font=(FONT_MAIN, 12), fg="#64748b", bg="#f0f4f8").pack()

    main_box = tk.Frame(scroll_frame, bg="white", padx=50, pady=30, highlightthickness=1, highlightbackground="#d1d5db")
    main_box.pack(pady=30)
    
    tk.Label(main_box, text=ICON.get(d['weather'][0]['main'], "🌡"), font=(FONT_MAIN, 80), bg="white", fg=PRIMARY).pack()
    tk.Label(main_box, text=f"{round(d['main']['temp'])}°C", font=(FONT_MAIN, 60, "bold"), bg="white", fg=TEXT_DARK).pack()
    tk.Label(main_box, text=d['weather'][0]['description'].upper(), font=(FONT_MAIN, 14, "bold"), bg="white", fg="#94a3b8").pack()

    grid_frame = tk.Frame(scroll_frame, bg="#f0f4f8")
    grid_frame.pack(pady=20)
    metrics = [("💧 Humidity", f"{d['main']['humidity']}%"), ("🌬 Wind", f"{d['wind']['speed']}m/s"), 
               ("🌡 Feels", f"{round(d['main']['feels_like'])}°"), ("📊 Pressure", f"{d['main']['pressure']}hPa")]

    for i, (m, v) in enumerate(metrics):
        f = tk.Frame(grid_frame, bg="white", padx=30, pady=20, borderwidth=1, relief="solid", highlightthickness=1, highlightbackground="#e2e8f0")
        f.grid(row=i//2, column=i%2, padx=10, pady=10)
        tk.Label(f, text=m, bg="white", fg="#64748b", font=(FONT_MAIN, 10)).pack()
        tk.Label(f, text=v, bg="white", fg=TEXT_DARK, font=(FONT_MAIN, 16, "bold")).pack()

    tk.Label(scroll_frame, text="Next 5 Days", font=(FONT_MAIN, 20, "bold"), bg="#f0f4f8", fg=TEXT_DARK).pack(pady=20)
    forecast_box = tk.Frame(scroll_frame, bg="#f0f4f8")
    forecast_box.pack(pady=10)

    for day in fdata[:5]:
        df = tk.Frame(forecast_box, bg="white", padx=20, pady=15, highlightthickness=1, highlightbackground="#e2e8f0")
        df.pack(side="left", padx=5)
        day_name = datetime.datetime.fromtimestamp(day["dt"]).strftime("%a")
        tk.Label(df, text=day_name, bg="white", font=(FONT_MAIN, 10, "bold")).pack()
        tk.Label(df, text=ICON.get(day['weather'][0]['main'], "☁"), bg="white", font=(FONT_MAIN, 20), fg=PRIMARY).pack()
        tk.Label(df, text=f"{round(day['main']['temp'])}°", bg="white", font=(FONT_MAIN, 14, "bold")).pack()

    tk.Button(scroll_frame, text="Close", command=win.destroy, bg="#ef4444", fg="white", font=(FONT_MAIN, 12, "bold"), relief="flat", padx=30, pady=10, cursor="hand2").pack(pady=40)

# --- Main App ---
root = tk.Tk()
root.title("SkyCast Premium")
root.state("zoomed")

# STYLING THE DROPDOWN POPUP
# This part styles the list that appears when you click the dropdown
root.option_add("*TCombobox*Listbox.font", (FONT_MAIN, 12))
root.option_add("*TCombobox*Listbox.background", "white")
root.option_add("*TCombobox*Listbox.foreground", TEXT_DARK)
root.option_add("*TCombobox*Listbox.selectBackground", PRIMARY)
root.option_add("*TCombobox*Listbox.selectForeground", "white")

style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox", 
                fieldbackground="white", 
                background="white", 
                foreground=TEXT_DARK, 
                padding=10)

W, H = root.winfo_screenwidth(), root.winfo_screenheight()
city_var = tk.StringVar()
cities = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad", "Jaipur"]

grad = create_gradient_bg(W, H, (230, 240, 255), (100, 150, 255))
bg_photo = ImageTk.PhotoImage(grad)
tk.Label(root, image=bg_photo).place(x=0, y=0, relwidth=1, relheight=1)

card = tk.Frame(root, bg="white", padx=50, pady=40, highlightthickness=1, highlightbackground="#e2e8f0")
card.place(relx=0.5, rely=0.45, anchor="center")

tk.Label(card, text="SkyCast", font=(FONT_MAIN, 45, "bold"), fg=PRIMARY, bg="white").pack()
tk.Label(card, text="Experience real-time weather clarity", font=(FONT_MAIN, 12), fg="#64748b", bg="white").pack(pady=(0, 30))

# THE STYLED DROPDOWN
box = ttk.Combobox(card, textvariable=city_var, values=cities, font=(FONT_MAIN, 14), width=25, justify="center")
box.pack(pady=10)
box.focus()

status_label = tk.Label(card, text="Select a city to begin", font=(FONT_MAIN, 9), bg="white", fg="#94a3b8")
status_label.pack(pady=5)

tk.Button(card, text="Detect My Location 📍", command=detect, bg=ACCENT, fg="white", font=(FONT_MAIN, 11, "bold"), relief="flat", width=25, pady=12, cursor="hand2").pack(pady=5)
tk.Button(card, text="Get Weather Report 🌦", command=get_weather, bg=PRIMARY, fg="white", font=(FONT_MAIN, 11, "bold"), relief="flat", width=25, pady=12, cursor="hand2").pack(pady=10)

root.bind('<Return>', get_weather)
root.mainloop()