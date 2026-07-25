"""Billing and Invoice management frame for WellCare Hospital System."""

from tkinter import messagebox
from typing import Any

import customtkinter as ctk
from src.wellcare.models import Bill, PaymentStatus
from src.wellcare.ui import KPICard, Theme, ToastNotification
from src.wellcare.utils.pdf import generate_invoice_pdf


class BillingFrame(ctk.CTkFrame):
    """Frame for generating invoices, reviewing receipts, and tracking clinic revenue."""

    def __init__(self, master: Any, controller: Any) -> None:
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self._build_ui()
        self.load_billing_data()

    def _build_ui(self) -> None:
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(15, 10), sticky="ew")

        ctk.CTkLabel(
            header_frame,
            text="💳 Patient Billing & Invoicing",
            font=Theme.FONT_HEADING,
            text_color=Theme.PRIMARY,
        ).pack(side="left", padx=15)

        # Financial KPI Summary Row
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_revenue = KPICard(
            self.kpi_frame,
            title="Total Revenue",
            value="$0.00",
            icon="💰",
            accent_color=Theme.SUCCESS,
        )
        self.kpi_revenue.grid(row=0, column=0, padx=5, sticky="ew")

        self.kpi_pending = KPICard(
            self.kpi_frame,
            title="Pending Due",
            value="$0.00",
            icon="⌛",
            accent_color=Theme.WARNING,
        )
        self.kpi_pending.grid(row=0, column=1, padx=5, sticky="ew")

        self.kpi_paid_count = KPICard(
            self.kpi_frame,
            title="Paid Invoices",
            value="0",
            icon="✅",
            accent_color=Theme.PRIMARY_ACCENT,
        )
        self.kpi_paid_count.grid(row=0, column=2, padx=5, sticky="ew")

        self.kpi_pending_count = KPICard(
            self.kpi_frame,
            title="Unpaid Count",
            value="0",
            icon="⚠️",
            accent_color=Theme.DANGER,
        )
        self.kpi_pending_count.grid(row=0, column=3, padx=5, sticky="ew")

        # Left Column: Add Invoice Form Card
        form_card = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=Theme.RADIUS_CARD,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
        )
        form_card.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")

        ctk.CTkLabel(
            form_card,
            text="Generate New Invoice",
            font=Theme.FONT_SUBHEADING,
            text_color=Theme.PRIMARY_ACCENT,
        ).pack(anchor="w", padx=15, pady=(15, 10))

        ctk.CTkLabel(form_card, text="Patient ID:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.patient_id_entry = ctk.CTkEntry(form_card, placeholder_text="e.g. 1", height=34)
        self.patient_id_entry.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Billing Amount ($):", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.amount_entry = ctk.CTkEntry(form_card, placeholder_text="e.g. 150.00", height=34)
        self.amount_entry.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Description / Services:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.desc_entry = ctk.CTkEntry(
            form_card, placeholder_text="e.g. Consultation & Blood Test", height=34
        )
        self.desc_entry.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(form_card, text="Payment Status:", font=Theme.FONT_BODY_BOLD).pack(
            anchor="w", padx=15
        )
        self.status_combo = ctk.CTkComboBox(
            form_card,
            values=["Pending", "Paid", "Partial"],
            height=34,
        )
        self.status_combo.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            form_card,
            text="💰 Generate Invoice",
            command=self._create_bill_action,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            font=Theme.FONT_BODY_BOLD,
            height=38,
        ).pack(fill="x", padx=15, pady=(0, 20))

        # Right Column: Invoice History List
        list_card = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=Theme.RADIUS_CARD,
            border_width=1,
            border_color=Theme.BORDER_LIGHT,
        )
        list_card.grid(row=2, column=1, padx=15, pady=10, sticky="nsew")
        list_card.grid_columnconfigure(0, weight=1)

        filter_frame = ctk.CTkFrame(list_card, fg_color="transparent")
        filter_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            filter_frame,
            text="Hospital Invoices & Receivables",
            font=Theme.FONT_SUBHEADING,
            text_color=Theme.PRIMARY_ACCENT,
        ).pack(side="left")

        ctk.CTkButton(
            filter_frame,
            text="🔄 Refresh",
            width=80,
            command=self.load_billing_data,
            fg_color=Theme.PRIMARY_ACCENT,
            height=30,
        ).pack(side="right")

        self.list_box = ctk.CTkTextbox(
            list_card,
            font=Theme.FONT_MONO,
            height=320,
        )
        self.list_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Bottom Quick Action Bar
        action_bar = ctk.CTkFrame(list_card, fg_color="transparent")
        action_bar.pack(fill="x", padx=15, pady=(0, 15))

        self.bill_id_entry = ctk.CTkEntry(
            action_bar, placeholder_text="Invoice ID", width=90, height=32
        )
        self.bill_id_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            action_bar,
            text="Mark Paid ✅",
            command=self._mark_paid_action,
            fg_color=Theme.SUCCESS,
            width=100,
            height=32,
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            action_bar,
            text="Print Receipt 📄",
            command=self._print_invoice_pdf_action,
            fg_color=Theme.PRIMARY_ACCENT,
            width=120,
            height=32,
        ).pack(side="left", padx=5)

    def load_billing_data(self) -> None:
        """Fetch bills and update financial KPIs and list."""
        stats = self.controller.db.get_billing_stats()
        self.kpi_revenue.update_value(f"${stats['total_revenue']:.2f}")
        self.kpi_pending.update_value(f"${stats['pending_amount']:.2f}")
        self.kpi_paid_count.update_value(str(stats["paid_count"]))
        self.kpi_pending_count.update_value(str(stats["pending_count"]))

        self.list_box.configure(state="normal")
        self.list_box.delete("1.0", "end")

        records = self.controller.db.get_bills()
        if records:
            h = (
                f"{'Inv#':<5} | {'Patient Name':<18} | {'Amount':<10} | "
                f"{'Status':<10} | {'Description'}\n"
            )
            self.list_box.insert("end", h + ("─" * 75) + "\n")
            for r in records:
                bid, _pid, pname, _aid, amount, desc, status, _created = r
                pname_str = pname or "Unknown"
                line = (
                    f"{bid:<5} | {pname_str[:18]:<18} | ${amount:<9.2f} | {status:<10} | {desc}\n"
                )
                self.list_box.insert("end", line)
        else:
            self.list_box.insert("end", "No billing records found.")

        self.list_box.configure(state="disabled")

    def _create_bill_action(self) -> None:
        pid_str = self.patient_id_entry.get().strip()
        amt_str = self.amount_entry.get().strip()
        desc = self.desc_entry.get().strip() or "General Consultation"
        status = self.status_combo.get().strip()

        if not pid_str.isdigit():
            messagebox.showerror("Error", "Patient ID must be a numeric integer.")
            return

        try:
            amt = float(amt_str)
            if amt <= 0 or amt > 1_000_000:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Billing amount must be a positive number up to $1,000,000."
            )
            return

        patient = self.controller.db.get_patient_by_id(int(pid_str))
        if not patient:
            messagebox.showerror("Error", f"Patient ID {pid_str} not found in database.")
            return

        bill = Bill(
            patient_id=int(pid_str),
            amount=amt,
            description=desc,
            status=status,
        )

        bill_id = self.controller.db.add_bill(bill)
        if bill_id:
            ToastNotification(
                self.controller,
                f"Invoice #{bill_id} generated for {patient.full_name}!",
                toast_type="success",
            )
            self.patient_id_entry.delete(0, "end")
            self.amount_entry.delete(0, "end")
            self.desc_entry.delete(0, "end")
            self.load_billing_data()
        else:
            messagebox.showerror("Error", "Failed to generate invoice.")

    def _mark_paid_action(self) -> None:
        bid_str = self.bill_id_entry.get().strip()
        if not bid_str.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric Invoice ID.")
            return

        bid = int(bid_str)
        if self.controller.db.update_bill_status(bid, PaymentStatus.PAID.value):
            ToastNotification(
                self.controller, f"Invoice #{bid} marked as Paid!", toast_type="success"
            )
            self.bill_id_entry.delete(0, "end")
            self.load_billing_data()
        else:
            messagebox.showerror("Error", f"Invoice #{bid} not found or status update failed.")

    def _print_invoice_pdf_action(self) -> None:
        bid_str = self.bill_id_entry.get().strip()
        if not bid_str.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric Invoice ID.")
            return

        bid = int(bid_str)
        bills = self.controller.db.get_bills()
        target_bill = next((b for b in bills if b[0] == bid), None)

        if target_bill:
            _, _pid, pname, _aid, amount, desc, status, _cat = target_bill
            pdf_path = generate_invoice_pdf(
                bill_id=bid,
                patient_name=pname or "Unknown Patient",
                amount=amount,
                description=desc or "",
                status=status or "Pending",
            )
            if pdf_path:
                ToastNotification(
                    self.controller, f"PDF Invoice generated for #{bid}!", toast_type="success"
                )
                messagebox.showinfo("Invoice Generated", f"Invoice saved to {pdf_path}")
            else:
                messagebox.showerror("Error", "Failed to generate PDF Invoice.")
        else:
            messagebox.showerror("Error", f"Invoice #{bid} not found in database.")
