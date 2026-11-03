"""Small Tkinter desktop client for the Photo CRM API."""
from __future__ import annotations

import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from google_integration.oauth_client import GoogleExport

API_URL = os.getenv("PHOTO_CRM_API", "http://127.0.0.1:8000")
KINDS = {
    "Клиенты": ("clients", ["id", "name", "email", "phone", "language", "status"]),
    "Съёмки": ("deals", ["id", "client_id", "title", "theme", "shoot_date", "status", "amount_eur"]),
    "Задачи": ("tasks", ["id", "client_id", "deal_id", "title", "due_date", "completed"]),
}


def api(method: str, path: str, payload: dict | None = None):
    data = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
    request = Request(f"{API_URL}{path}", data=data, method=method,
                      headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=8) as response:
            return json.loads(response.read()) if response.status != 204 else None
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"API вернул {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Не удалось подключиться к API {API_URL}: {exc.reason}") from exc


class CRMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo CRM · Germany demo")
        self.geometry("1080x620")
        self.current_label = "Клиенты"
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        self.kind = ttk.Combobox(top, state="readonly", values=list(KINDS), width=18)
        self.kind.set(self.current_label)
        self.kind.pack(side="left")
        self.kind.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        ttk.Button(top, text="Обновить", command=self.refresh).pack(side="left", padx=6)
        ttk.Button(top, text="Добавить", command=self.add_record).pack(side="left")
        ttk.Button(top, text="Удалить выбранное", command=self.delete_record).pack(side="left", padx=6)
        ttk.Button(top, text="Экспорт в Google Sheets", command=self.export_all).pack(side="right")
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        self.status = ttk.Label(self, text=f"API: {API_URL}", anchor="w", padding=(10, 4))
        self.status.pack(fill="x")
        self.refresh()

    def refresh(self):
        label = self.kind.get()
        endpoint, columns = KINDS[label]
        try:
            rows = api("GET", f"/{endpoint}?limit=1000")
            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = columns
            for column in columns:
                self.tree.heading(column, text=column)
                self.tree.column(column, width=145, minwidth=80)
            for row in rows:
                self.tree.insert("", "end", iid=str(row["id"]), values=[row.get(k, "") for k in columns])
            self.status.config(text=f"{label}: {len(rows)} записей · API: {API_URL}")
        except Exception as exc:
            self.status.config(text=str(exc))

    def add_record(self):
        label = self.kind.get()
        if label == "Клиенты":
            name = simpledialog.askstring("Новый клиент", "Имя:", parent=self)
            if not name: return
            payload = {"name": name, "language": "DE"}
        elif label == "Съёмки":
            title = simpledialog.askstring("Новая съёмка", "Название:", parent=self)
            if not title: return
            payload = {"title": title}
        else:
            title = simpledialog.askstring("Новая задача", "Название:", parent=self)
            if not title: return
            payload = {"title": title}
        endpoint, _ = KINDS[label]
        try:
            api("POST", f"/{endpoint}", payload)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Не удалось создать запись", str(exc), parent=self)

    def delete_record(self):
        selected = self.tree.selection()
        if not selected: return
        if not messagebox.askyesno("Удаление", "Удалить выбранную запись?", parent=self): return
        endpoint, _ = KINDS[self.kind.get()]
        try:
            api("DELETE", f"/{endpoint}/{selected[0]}")
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Не удалось удалить запись", str(exc), parent=self)

    def export_all(self):
        try:
            exporter = GoogleExport()
            links = []
            for label, (endpoint, columns) in KINDS.items():
                rows = api("GET", f"/{endpoint}?limit=1000")
                title = f"Photo CRM — {endpoint} — {__import__('datetime').date.today().isoformat()}"
                link = exporter.create_report(title, columns, [[row.get(k, "") for k in columns] for row in rows])
                links.append(f"{label}: {link}")
            messagebox.showinfo("Экспорт готов", "\n\n".join(links), parent=self)
        except Exception as exc:
            messagebox.showerror("Ошибка экспорта", str(exc), parent=self)


if __name__ == "__main__":
    CRMApp().mainloop()
