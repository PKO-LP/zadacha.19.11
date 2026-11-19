import tkinter as tk
from tkinter import messagebox, ttk

# Справочник базовых цен за пиццу 25 см (в рублях)
PIZZA_PRICES = {
    "Маргарита": 450,
    "Пепперони": 550,
    "Четыре сыра": 600,
    "Гавайская": 520,
    "Мясная": 620,
}

# Коэффициенты стоимости в зависимости от размера
SIZE_COEFFS = {
    "Маленькая 25 см": 1.0,
    "Средняя 30 см": 1.3,
    "Большая 35 см": 1.6,
}

DEFAULT_PIZZA = "Маргарита"
DEFAULT_SIZE = "Маленькая 25 см"


class PizzaOrderApp:

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("MyПицца — Учёт заказов (Спринт 1)")
        self.root.geometry("820x500")
        self.root.resizable(False, False)

        # Список словарей для хранения заказов в памяти
        self.orders: list[dict] = []
        self.next_id: int = 1

        self._build_ui()
        self._update_preview_sum()

    def _build_ui(self) -> None:
        # Верхняя панель: форма ввода заказа
        form_frame = ttk.LabelFrame(
            self.root, text="Новый заказ", padding=(12, 8)
        )
        form_frame.pack(fill="x", padx=12, pady=10)

        ttk.Label(form_frame, text="Пицца:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.pizza_var = tk.StringVar(value=DEFAULT_PIZZA)
        self.pizza_combo = ttk.Combobox(
            form_frame,
            textvariable=self.pizza_var,
            values=list(PIZZA_PRICES.keys()),
            state="readonly",
            width=18,
        )
        self.pizza_combo.grid(row=0, column=1, padx=5, pady=5)
        self.pizza_combo.bind(
            "<<ComboboxSelected>>", lambda e: self._update_preview_sum()
        )

        ttk.Label(form_frame, text="Размер:").grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )
        self.size_var = tk.StringVar(value=DEFAULT_SIZE)
        self.size_combo = ttk.Combobox(
            form_frame,
            textvariable=self.size_var,
            values=list(SIZE_COEFFS.keys()),
            state="readonly",
            width=18,
        )
        self.size_combo.grid(row=0, column=3, padx=5, pady=5)
        self.size_combo.bind(
            "<<ComboboxSelected>>", lambda e: self._update_preview_sum()
        )

        ttk.Label(form_frame, text="Количество:").grid(
            row=0, column=4, padx=5, pady=5, sticky="w"
        )
        self.qty_var = tk.StringVar(value="1")
        self.qty_entry = ttk.Entry(
            form_frame, textvariable=self.qty_var, width=8
        )
        self.qty_entry.grid(row=0, column=5, padx=5, pady=5)
        self.qty_entry.bind("<KeyRelease>", lambda e: self._update_preview_sum())

        # Метка предварительного расчёта суммы
        self.preview_label = ttk.Label(
            form_frame, text="Итого: 450 ₽", font=("Segoe UI", 10, "bold")
        )
        self.preview_label.grid(
            row=1, column=0, columnspan=3, padx=5, pady=8, sticky="w"
        )

        # Кнопки формы
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=1, column=3, columnspan=3, padx=5, pady=8, sticky="e")

        ttk.Button(
            btn_frame, text="Добавить заказ", command=self.add_order
        ).pack(side="left", padx=4)
        ttk.Button(
            btn_frame, text="Очистить форму", command=self.clear_form
        ).pack(side="left", padx=4)

        # Нижняя панель: таблица заказов
        table_frame = ttk.LabelFrame(
            self.root, text="Список заказов", padding=(12, 8)
        )
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        columns = ("id", "pizza", "size", "qty", "total", "status")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=13
        )

        self.tree.heading("id", text="№")
        self.tree.heading("pizza", text="Пицца")
        self.tree.heading("size", text="Размер")
        self.tree.heading("qty", text="Кол-во")
        self.tree.heading("total", text="Сумма (₽)")
        self.tree.heading("status", text="Статус")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("pizza", width=180, anchor="w")
        self.tree.column("size", width=160, anchor="center")
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("total", width=110, anchor="e")
        self.tree.column("status", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _calculate_total(self, pizza: str, size: str, qty: int) -> int:
        base_price = PIZZA_PRICES[pizza]
        coeff = SIZE_COEFFS[size]
        return round(base_price * coeff) * qty

    def _update_preview_sum(self) -> None:
        pizza = self.pizza_var.get()
        size = self.size_var.get()
        raw_qty = self.qty_var.get().strip()

        if raw_qty.isdigit() and 1 <= int(raw_qty) <= 50:
            total = self._calculate_total(pizza, size, int(raw_qty))
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
            messagebox.showwarning(
                "Ошибка ввода", "Количество должно быть целым числом."
            )
            return None
        if qty < 1 or qty > 50:
            messagebox.showwarning(
                "Ошибка ввода", "Количество должно быть от 1 до 50."
            )
            return None
        return qty

    def add_order(self) -> None:
        qty = self._validate_qty()
        if qty is None:
            return

        pizza = self.pizza_var.get()
        size = self.size_var.get()
        total = self._calculate_total(pizza, size, qty)

        order = {
            "id": self.next_id,
            "pizza": pizza,
            "size": size,
            "qty": qty,
            "total": total,
            "status": "Готовится",
        }
        self.orders.append(order)
        self.next_id += 1

        self._refresh_table()
        self.clear_form()

    def clear_form(self) -> None:
        self.pizza_var.set(DEFAULT_PIZZA)
        self.size_var.set(DEFAULT_SIZE)
        self.qty_var.set("1")
        self._update_preview_sum()

    def _refresh_table(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)

        for order in self.orders:
            self.tree.insert(
                "",
                "end",
                values=(
                    order["id"],
                    order["pizza"],
                    order["size"],
                    order["qty"],
                    order["total"],
                    order["status"],
                ),
            )


def main() -> None:
    root = tk.Tk()
    PizzaOrderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
