import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import json, os, datetime, random
import matplotlib.pyplot as plt
from tkcalendar import Calendar
from openpyxl import Workbook
from plyer import notification

# ---------- Global Variables ----------
DATA_FILE = 'data.json'
current_user = None
data = {}

# ---------- Helper Functions ----------
def load_data():
    global data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {}

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def login_user():
    global current_user
    username = simpledialog.askstring("Login", "Enter your username:")
    if not username:
        messagebox.showerror("Error", "Username is required.")
        return
    if username not in data:
        data[username] = {
            "habits": [],
            "logs": {},
            "streak": 0,
            "notes": "",
            "moods": {},
            "progress": {}
        }
    current_user = username
    save_data()
    show_home()

def update_ui():
    habit_listbox.delete(0, tk.END)
    for habit in data[current_user]["habits"]:
        habit_listbox.insert(tk.END, habit)

def add_habit():
    habit = habit_input.get()
    if habit and habit not in data[current_user]["habits"]:
        data[current_user]["habits"].append(habit)
        data[current_user]["progress"][habit] = 0
        save_data()
        update_ui()
        habit_input.delete(0, tk.END)

def remove_habit():
    try:
        sel = habit_listbox.curselection()
        if sel:
            habit = habit_listbox.get(sel)
            data[current_user]["habits"].remove(habit)
            data[current_user]["progress"].pop(habit, None)
            save_data()
            update_ui()
    except:
        messagebox.showerror("Error", "Select a habit to remove.")

def log_today():
    today = str(datetime.date.today())
    if today not in data[current_user]["logs"]:
        data[current_user]["logs"][today] = []
    selected = [habit_listbox.get(i) for i in habit_listbox.curselection()]
    data[current_user]["logs"][today].extend(selected)
    data[current_user]["logs"][today] = list(set(data[current_user]["logs"][today]))
    save_data()
    update_streak()
    messagebox.showinfo("Logged", "Today's habits have been logged.")

def update_streak():
    logs = data[current_user]["logs"]
    streak = 0
    today = datetime.date.today()
    for i in range(15):
        date_str = str(today - datetime.timedelta(days=i))
        if date_str in logs and logs[date_str]:
            streak += 1
        else:
            break
    data[current_user]["streak"] = streak
    save_data()
    streak_label.config(text=f"Current Streak: {streak} days")
    if streak in [3, 7, 15]:
        notification.notify(
            title="Habit Streak",
            message=f"Awesome! You've reached a {streak}-day streak!",
            timeout=5
        )

def show_calendar():
    top = tk.Toplevel(root)
    top.title("Habit Log Calendar")
    cal = Calendar(top, selectmode='day')
    cal.pack(pady=10)

    def view_logs():
        sel = cal.get_date()
        logs = data[current_user]["logs"].get(sel, [])
        messagebox.showinfo("Logs", f"Habits on {sel}:\n" + "\n".join(logs) if logs else "No logs.")

    tk.Button(top, text="View Logs", command=view_logs).pack(pady=5)

def export_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Habit Logs"
    ws.append(["Date", "Habits"])
    for date, habits in data[current_user]["logs"].items():
        ws.append([date, ", ".join(habits)])
    file = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if file:
        wb.save(file)
        messagebox.showinfo("Exported", f"Data saved to {file}")

def weekly_graph():
    logs = data[current_user]["logs"]
    today = datetime.date.today()
    week_data = {}
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        date_str = str(date)
        week_data[date_str] = len(logs.get(date_str, []))

    plt.bar(week_data.keys(), week_data.values(), color="#F7C59F")
    plt.xticks(rotation=45)
    plt.title("Weekly Habit Summary")
    plt.ylabel("Completed Habits")
    plt.tight_layout()
    plt.show()

def show_notes():
    notes_window = tk.Toplevel(root)
    notes_window.title("Mood & Note Tracker")

    mood_label = tk.Label(notes_window, text="Select Today's Mood:")
    mood_label.pack(pady=5)

    moods = ["Happy", "Sad", "Neutral", "Excited", "Stressed", "Calm"]
    mood_var = tk.StringVar(notes_window)
    mood_var.set(moods[0])

    mood_menu = tk.OptionMenu(notes_window, mood_var, *moods)
    mood_menu.pack(pady=5)

    note_label = tk.Label(notes_window, text="Note:")
    note_label.pack(pady=5)
    note_text = tk.Text(notes_window, height=10, width=40)
    note_text.insert(tk.END, data[current_user].get("notes", ""))
    note_text.pack(pady=5)

    def save_notes():
        mood = mood_var.get()
        data[current_user]["notes"] = note_text.get("1.0", tk.END).strip()
        data[current_user]["moods"][str(datetime.date.today())] = mood
        save_data()
        messagebox.showinfo("Saved", "Mood and note saved.")

    tk.Button(notes_window, text="Save", command=save_notes).pack(pady=10)
    tk.Button(notes_window, text="Return Home", command=notes_window.destroy).pack(pady=5)

def show_progress_pie():
    progress = data[current_user].get("progress", {})
    if not progress or all(v == 0 for v in progress.values()):
        messagebox.showinfo("No Data", "No progress data to display.")
        return

    labels = list(progress.keys())
    sizes = list(progress.values())

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    plt.title("Habit Progress Distribution")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

def add_progress():
    selected = [habit_listbox.get(i) for i in habit_listbox.curselection()]
    if not selected:
        messagebox.showwarning("No Habit", "Please select at least one habit.")
        return
    for habit in selected:
        try:
            progress = simpledialog.askinteger("Progress Input", f"Enter progress for '{habit}' (e.g., 0-100):", minvalue=0)
            if progress is not None:
                data[current_user]["progress"][habit] = progress
        except:
            continue
    save_data()
    messagebox.showinfo("Saved", "Progress updated successfully.")

def show_home():
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=random.choice(pastel_colors))
    tk.Label(root, text="Welcome to Swamini Habit Tracker", font=("Arial", 16, "bold"), bg=root["bg"]).pack(pady=20)

    tk.Button(root, text="1. Habit Manager", font=("Arial", 12), command=habit_manager).pack(pady=10)
    tk.Button(root, text="2. Mood & Note Tracker", font=("Arial", 12), command=show_notes).pack(pady=10)
    tk.Button(root, text="3. AI Habit Suggestions", font=("Arial", 12), command=ai_suggestions).pack(pady=10)

def habit_manager():
    manager = tk.Toplevel(root)
    manager.title("Habit Manager")

    global habit_input, habit_listbox, streak_label

    tk.Label(manager, text="Enter Habit:").pack(pady=5)
    habit_input = tk.Entry(manager, width=30)
    habit_input.pack(pady=5)
    tk.Button(manager, text="Add Habit", command=add_habit).pack(pady=5)

    habit_listbox = tk.Listbox(manager, width=40, height=10, selectmode=tk.MULTIPLE)
    habit_listbox.pack(pady=5)
    update_ui()

    tk.Button(manager, text="Remove Habit", command=remove_habit).pack(pady=5)
    tk.Button(manager, text="Log Today's Habits", command=log_today).pack(pady=5)
    tk.Button(manager, text="Add Progress", command=add_progress).pack(pady=5)
    tk.Button(manager, text="Show Progress Pie Chart", command=show_progress_pie).pack(pady=5)
    tk.Button(manager, text="View Weekly Graph", command=weekly_graph).pack(pady=5)
    tk.Button(manager, text="View Calendar Logs", command=show_calendar).pack(pady=5)
    tk.Button(manager, text="Export to Excel", command=export_excel).pack(pady=5)

    streak_label = tk.Label(manager, text="Current Streak: 0 days")
    streak_label.pack(pady=5)
    update_streak()

    tk.Button(manager, text="Back to Home", command=manager.destroy).pack(pady=10)

def ai_suggestions():
    suggestions = [
        "Try meditating for 5 minutes daily.",
        "Drink at least 8 glasses of water today.",
        "Walk for 10 minutes every hour.",
        "Try stretching every morning."
    ]
    suggestion = random.choice(suggestions)
    messagebox.showinfo("AI Habit Suggestion", suggestion)

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("Swamini Habit Tracker")
root.geometry("700x800")

pastel_colors = ["#FFF8DC", "#FFFAF0", "#FFFFE0", "#FDFD96", "#FAFAD2"]

load_data()
login_user()
root.mainloop()
