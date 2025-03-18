import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox
from datetime import datetime

# 設定 SQLite 資料庫
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    amount REAL,
    category TEXT,
    type TEXT,  -- '收入' or '支出'
    date TEXT   -- 記錄交易日期
)
''')

conn.commit()

exp = True


def changetoexp():
    global exp
    exp = True
    print(exp)
    load_expenses()


def changetoinc():
    global exp
    exp = False
    print(exp)
    load_expenses()


# 顯示記帳紀錄
def load_expenses():
    selected_month = month_entry.get()
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("SELECT name, amount, category, type, date FROM expenses")
    records = cursor.fetchall()

    total_income = 0
    total_expense = 0
    year_now = selected_month[0:4]
    month_now = selected_month[6] if selected_month[5] == "0" else selected_month[5:7]
    for record in records:
        name, amount, category, exp_type, date = record

        if date.startswith(f"{year_now}/{(month_now)}"):
            if exp_type == "收入":
                total_income += amount
                if not exp:
                    tree.insert("", "end", values=(
                        name, f"${amount:.2f}", category, exp_type, date), tags=("income",))
            else:
                total_expense += amount
                if exp:
                    tree.insert("", "end", values=(
                        name, f"${amount:.2f}", category, exp_type, date), tags=("expense",))

    balance_label.config(
        text=f"💰 總收入: ${total_income:.2f}   💸 總支出: ${total_expense:.2f}   📊 結餘: ${total_income - total_expense:.2f}")

# 新增記帳紀錄


def add_expense():
    name = entry_name.get()
    amount = entry_amount.get()
    category = entry_category.get()
    exp_type = type_var.get()
    date = date_entry.entry.get()  # 使用者選擇的日期

    if name and amount and category and date:
        try:
            amount = float(amount)
            # 檢查是否為正數
            if amount < 0:
                messagebox.showerror("輸入錯誤", "金額不可為小於 0 的負數")
                return
            # 檢查小數點後不超過兩位數
            if len(amount_str := str(amount).split(".")[-1]) > 2:
                messagebox.showerror("輸入錯誤", "金額最多只能有兩位小數")
                return
            cursor.execute("INSERT INTO expenses (name, amount, category, type, date) VALUES (?, ?, ?, ?, ?)",
                           (name, amount, category, exp_type, date))
            conn.commit()
            entry_name.delete(0, ttk.END)
            entry_amount.delete(0, ttk.END)
            entry_category.delete(0, ttk.END)
            load_expenses()
        except ValueError:
            messagebox.showerror("輸入錯誤", "金額請輸入數字")
    else:
        messagebox.showerror("輸入錯誤", "請填寫所有欄位")

# 刪除選中的記帳紀錄


def delete_expense():
    selected_item = tree.selection()
    if selected_item:
        item_values = tree.item(selected_item, "values")
        name, amount, category, exp_type, date = item_values
        cursor.execute("DELETE FROM expenses WHERE name = ? AND amount = ? AND category = ? AND type = ? AND date = ?",
                       (name, amount.replace("$", ""), category, exp_type, date))
        conn.commit()
        load_expenses()
    else:
        messagebox.showerror("刪除錯誤", "請選擇要刪除的項目")


# 追蹤排序狀態
sort_ascending = True  # 預設為小到大


def sort_expenses_by_amount():
    global sort_ascending  # 使用全域變數來切換排序方式
    records = []

    # 取得表格內的所有資料
    for item in tree.get_children():
        records.append(tree.item(item, "values"))

    # 轉換金額為數字並排序
    records.sort(key=lambda x: float(
        x[1].replace("$", "")), reverse=not sort_ascending)

    # 切換排序方式，下次點擊時相反
    sort_ascending = not sort_ascending

    # 清除表格內的內容並重新插入排序後的資料
    for item in tree.get_children():
        tree.delete(item)

    for record in records:
        name, amount, category, exp_type, date = record
        tag = "income" if exp_type == "收入" else "expense"
        tree.insert("", "end", values=(
            name, amount, category, exp_type, date), tags=(tag,))


sort_date_ascending = True


def sort_expenses_by_date():
    global sort_date_ascending
    records = [tree.item(item, "values") for item in tree.get_children()]
    records.sort(key=lambda x: datetime.strptime(
        x[4], "%Y/%m/%d"), reverse=not sort_date_ascending)
    sort_date_ascending = not sort_date_ascending
    refresh_tree(records)


def refresh_tree(records):
    for item in tree.get_children():
        tree.delete(item)
    for record in records:
        tree.insert("", "end", values=record, tags=(
            "income" if record[3] == "收入" else "expense",))


def on_amount_click(event):
    item = tree.identify_row(event.y)  # 找到被點擊的 row
    column = tree.identify_column(event.x)  # 找到被點擊的 column
    if column == "#2" and not (item):  # #2 代表「金額」欄位
        sort_expenses_by_amount()
    elif column == "#5" and not (item):  # #2 代表「金額」欄位
        sort_expenses_by_date()


# GUI 介面
root = ttk.Window(themename="darkly")  # 設定主題
root.title("💰 記帳本")
root.geometry("1100x750")

# 設定介面元件
frame = ttk.Frame(root)
frame.pack(pady=10, padx=10)

# 輸入框
ttk.Label(frame, text="項目名稱:").grid(row=0, column=0, padx=5, pady=5)
entry_name = ttk.Entry(frame)
entry_name.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame, text="金額:").grid(row=1, column=0, padx=5, pady=5)
entry_amount = ttk.Entry(frame)
entry_amount.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame, text="類別:").grid(row=2, column=0, padx=5, pady=5)
entry_category = ttk.Entry(frame)
entry_category.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame, text="類型:").grid(row=3, column=0, padx=5, pady=5)
type_var = ttk.StringVar(value="支出")
type_dropdown = ttk.Combobox(frame, textvariable=type_var, values=["收入", "支出"])
type_dropdown.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(frame, text="日期:").grid(row=4, column=0, padx=5, pady=5)
date_entry = DateEntry(frame, bootstyle=PRIMARY)
date_entry.grid(row=4, column=1, padx=5, pady=5)

# 篩選月份
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=5)

ttk.Button(btn_frame, text="➕ 新增記帳", command=add_expense,
           bootstyle=SUCCESS).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="🗑️ 刪除選擇", command=delete_expense,
           bootstyle=DANGER).grid(row=0, column=1, padx=5)

# 月份選擇
ttk.Label(btn_frame, text="選擇月份:").grid(row=0, column=2, padx=5, pady=5)
# 範圍從 2000-01 到現在的月份
month_entry = ttk.Combobox(btn_frame, values=[
                           f"{year}-{str(month).zfill(2)}" for year in range(2000, datetime.now().year + 1) for month in range(1, 13)])
month_entry.grid(row=0, column=3, padx=5, pady=5)
# 預設選擇當前年份和月份
month_entry.current((datetime.now().year - 2000) *
                    12 + datetime.now().month - 1)
ttk.Button(btn_frame, text="📅 查看月份", command=load_expenses,
           bootstyle=PRIMARY).grid(row=0, column=4, padx=5)

ttk.Button(btn_frame, text="💰 收入", command=changetoinc,
           bootstyle=SUCCESS).grid(row=0, column=5, padx=5)
ttk.Button(btn_frame, text="💸 支出", command=changetoexp,
           bootstyle=DANGER).grid(row=0, column=6, padx=5)


# 建立表格
columns = ("名稱", "金額", "類別", "類型", "日期")
tree = ttk.Treeview(root, columns=columns, show="headings")

# 設定 Treeview 標題
tree.heading("名稱", text="名稱")
tree.heading("金額", text="金額 🔽")  # 讓 "金額" 標題不顯示，因為我們用 Frame 模擬
tree.heading("類別", text="類別")
tree.heading("類型", text="類型")
tree.heading("日期", text="日期 🔽")
tree.bind("<Button-1>", on_amount_click)
tree.pack(pady=10)

tree.tag_configure("income", foreground="green")
tree.tag_configure("expense", foreground="red")

balance_label = ttk.Label(
    root, text="💰 總收入: $0.00   💸 總支出: $0.00   📊 結餘: $0.00", bootstyle="inverse-dark")
balance_label.pack(pady=10)

# 載入現有記帳紀錄
load_expenses()

root.mainloop()
