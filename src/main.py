import tkinter as tk
from tkinter import messagebox, ttk

PIZZA_PRICES = {
    "Маргарита": 450,
    "Пепперони": 550,
    "Четыре сыра": 600,
    "Гавайская": 520,
    "Мясная": 620,
}

SIZE_COEFFS = {
    "Маленькая 25 см": 1.0,
    "Средняя 30 см": 1.3,
    "Большая 35 см": 1.6,
}

STATUS_FLOW = ["Готовится", "Готов", "Выдан"]
DEFAULT_PIZZA = "Маргарита"
DEFAULT_SIZE = "Маленькая 25 см"


class PizzaOrderApp:

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("MyПицца — Учёт заказов")
        self.root.geometry("860x560")
        self.root.resizable(False, False)

        self.orders: list[dict] = []
        self.next_id: int = 1
        self.selected_order_id: int | None = None

        self._build_ui()
        self._update_preview_sum()

    def _build_ui(self) -> None:
        form_frame = ttk.LabelFrame(self.root, text="Форма заказа", padding=(12, 8))
        form_frame.pack(fill="x", padx=12, pady=(10, 6))

        ttk.Label(form_frame, text="Пицца:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.pizza_var = tk.StringVar(value=DEFAULT_PIZZA)
        self.pizza_combo = ttk.Combobox(
            form_frame, textvariable=self.pizza_var, values=list(PIZZA_PRICES.keys()), state="readonly", width=18
        )
        self.pizza_combo.grid(row=0, column=1, padx=5, pady=5)
        self.pizza_combo.bind("<<ComboboxSelected>>", lambda e: self._update_preview_sum())

        ttk.Label(form_frame, text="Размер:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.size_var = tk.StringVar(value=DEFAULT_SIZE)
        self.size_combo = ttk.Combobox(
            form_frame, textvariable=self.size_var, values=list(SIZE_COEFFS.keys()), state="readonly", width=18
        )
        self.size_combo.grid(row=0, column=3, padx=5, pady=5)
        self.size_combo.bind("<<ComboboxSelected>>", lambda e: self._update_preview_sum())

        ttk.Label(form_frame, text="Количество:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.qty_var = tk.StringVar(value="1")
        self.qty_entry = ttk.Entry(form_frame, textvariable=self.qty_var, width=8)
        self.qty_entry.grid(row=0, column=5, padx=5, pady=5)
        self.qty_entry.bind("<KeyRelease>", lambda e: self._update_preview_sum())

        self.preview_label = ttk.Label(form_frame, text="Итого: 450 ₽", font=("Segoe UI", 10, "bold"))
        self.preview_label.grid(row=1, column=0, columnspan=3, padx=5, pady=6, sticky="w")

        self.selected_label = ttk.Label(form_frame, text="Режим: новый заказ", foreground="#555555")
        self.selected_label.grid(row=1, column=3, columnspan=3, padx=5, pady=6, sticky="e")

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=6, padx=5, pady=(4, 2), sticky="w")
        ttk.Button(btn_frame, text="Добавить заказ", command=self.add_order).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="Сохранить изменения", command=self.update_order).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Следующий статус", command=self.advance_status).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Удалить заказ", command=self.delete_order).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Очистить форму", command=self.clear_form).pack(side="left", padx=6)
        filter_frame = ttk.LabelFrame(self.root, text="Поиск и фильтрация", padding=(12, 6))
        filter_frame.pack(fill="x", padx=12, pady=6)

        ttk.Label(filter_frame, text="Поиск (№ или пицца):").pack(side="left", padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=26)
        self.search_entry.pack(side="left", padx=6)
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_table())

        ttk.Label(filter_frame, text="Статус:").pack(side="left", padx=(14, 6))
        self.filter_status_var = tk.StringVar(value="Все")
        self.filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.filter_status_var, values=["Все"] + STATUS_FLOW, state="readonly", width=14
        )
        self.filter_combo.pack(side="left", padx=6)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_table())
        ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filters).pack(side="left", padx=10)

        table_frame = ttk.LabelFrame(self.root, text="Список заказов", padding=(12, 8))
        table_frame.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        columns = ("id", "pizza", "size", "qty", "total", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=13)
        for col, title, w, anc in [
            ("id", "№", 50, "center"),
            ("pizza", "Пицца", 190, "w"),
            ("size", "Размер", 170, "center"),
            ("qty", "Кол-во", 80, "center"),
            ("total", "Сумма (₽)", 120, "e"),
            ("status", "Статус", 150, "center"),
        ]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=w, anchor=anc)

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _calculate_total(self, pizza: str, size: str, qty: int) -> int:
        return round(PIZZA_PRICES[pizza] * SIZE_COEFFS[size]) * qty

    def _update_preview_sum(self) -> None:
        raw_qty = self.qty_var.get().strip()
        if raw_qty.isdigit() and 1 <= int(raw_qty) <= 50:
            total = self._calculate_total(self.pizza_var.get(), self.size_var.get(), int(raw_qty))
            self.preview_label.config(text=f"Итого: {total} ₽")
        else:
            self.preview_label.config(text="Итого: — (введите число от 1 до 50)")

    def _validate_qty(self) -> int | None:
        raw_qty = self.qty_var.get().strip()
        if not raw_qty:
            messagebox.showwarning("Ошибка ввода", "Укажите количество пицц.")
            return None
        try:
            qty = int(raw_qty)
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Количество должно быть целым числом.")
            return None
        if qty < 1 or qty > 50:
            messagebox.showwarning("Ошибка ввода", "Количество должно быть от 1 до 50.")
            return None
        return qty
    def _find_order_by_id(self, order_id: int) -> dict | None:
        return next((o for o in self.orders if o["id"] == order_id), None)

    def _on_row_select(self, _event: tk.Event) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        order = self._find_order_by_id(int(values[0]))
        if not order:
            return
        self.selected_order_id = order["id"]
        self.pizza_var.set(order["pizza"])
        self.size_var.set(order["size"])
        self.qty_var.set(str(order["qty"]))
        self._update_preview_sum()
        self.selected_label.config(text=f"Выбран заказ №{order['id']} ({order['status']})")

    def add_order(self) -> None:
        qty = self._validate_qty()
        if qty is None:
            return
        pizza, size = self.pizza_var.get(), self.size_var.get()
        self.orders.append({
            "id": self.next_id,
            "pizza": pizza,
            "size": size,
            "qty": qty,
            "total": self._calculate_total(pizza, size, qty),
            "status": STATUS_FLOW[0],
        })
        self.next_id += 1
        self._refresh_table()
        self.clear_form()

    def update_order(self) -> None:
        if self.selected_order_id is None:
            messagebox.showwarning("Заказ не выбран", "Выберите заказ в таблице.")
            return
        qty = self._validate_qty()
        order = self._find_order_by_id(self.selected_order_id)
        if qty is None or not order:
            return
        order["pizza"] = self.pizza_var.get()
        order["size"] = self.size_var.get()
        order["qty"] = qty
        order["total"] = self._calculate_total(order["pizza"], order["size"], qty)
        self._refresh_table()
        self.clear_form()

    def advance_status(self) -> None:
        if self.selected_order_id is None:
            messagebox.showwarning("Заказ не выбран", "Выберите заказ в таблице.")
            return
        order = self._find_order_by_id(self.selected_order_id)
        if not order:
            return
        idx = STATUS_FLOW.index(order["status"])
        if idx >= len(STATUS_FLOW) - 1:
            messagebox.showinfo("Финальный статус", f"Заказ №{order['id']} уже выдан.")
            return
        order["status"] = STATUS_FLOW[idx + 1]
        self._refresh_table()
        self.selected_label.config(text=f"Выбран заказ №{order['id']} ({order['status']})")

    def delete_order(self) -> None:
        if self.selected_order_id is None:
            messagebox.showwarning("Заказ не выбран", "Выберите заказ для удаления.")
            return
        order = self._find_order_by_id(self.selected_order_id)
        if not order:
            return
        if messagebox.askyesno("Подтверждение", f"Удалить заказ №{order['id']} ({order['pizza']})?"):
            self.orders = [o for o in self.orders if o["id"] != self.selected_order_id]
            self._refresh_table()
            self.clear_form()

    def clear_form(self) -> None:
        self.selected_order_id = None
        self.pizza_var.set(DEFAULT_PIZZA)
        self.size_var.set(DEFAULT_SIZE)
        self.qty_var.set("1")
        self._update_preview_sum()
        self.selected_label.config(text="Режим: новый заказ")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def reset_filters(self) -> None:
        self.search_var.set("")
        self.filter_status_var.set("Все")
        self._refresh_table()

    def _refresh_table(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        query = self.search_var.get().strip().lower()
        status_filter = self.filter_status_var.get()
        for o in self.orders:
            if status_filter != "Все" and o["status"] != status_filter:
                continue
            if query and query not in str(o["id"]) and query not in o["pizza"].lower():
                continue
            self.tree.insert("", "end", values=(o["id"], o["pizza"], o["size"], o["qty"], o["total"], o["status"]))


def main() -> None:
    root = tk.Tk()
    PizzaOrderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
