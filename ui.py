import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

import analysis
import visualization
import database
import reports


BASE_DIR = Path(__file__).resolve().parent


class MWCNTApplication(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title(
            "MWCNT Characterization and Analysis System"
        )

        self.geometry(
            "1350x820"
        )

        self.minsize(
            1100,
            700
        )

        self.configure(
            bg="#f4f6f8"
        )

        database.initialize_database()

        self.current_page = None

        self.setup_style()
        self.build_interface()

        self.show_dashboard()

    # ========================================================
    # STYLE
    # ========================================================

    def setup_style(self):

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            rowheight=32,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=(12, 8)
        )

        style.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 10)
        )

    # ========================================================
    # MAIN INTERFACE
    # ========================================================

    def build_interface(self):

        self.header = tk.Frame(
            self,
            bg="#17202a",
            height=78
        )

        self.header.pack(
            side="top",
            fill="x"
        )

        self.header.pack_propagate(False)

        title = tk.Label(
            self.header,
            text="MWCNT CHARACTERIZATION",
            bg="#17202a",
            fg="white",
            font=("Segoe UI", 20, "bold")
        )

        title.pack(
            side="left",
            padx=28
        )

        subtitle = tk.Label(
            self.header,
            text="Characterization, analysis and reporting system",
            bg="#17202a",
            fg="#bdc3c7",
            font=("Segoe UI", 10)
        )

        subtitle.pack(
            side="left",
            padx=8
        )

        body = tk.Frame(
            self,
            bg="#f4f6f8"
        )

        body.pack(
            fill="both",
            expand=True
        )

        self.sidebar = tk.Frame(
            body,
            bg="#202a35",
            width=230
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(
            body,
            bg="#f4f6f8"
        )

        self.content.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.build_sidebar()

    # ========================================================
    # SIDEBAR
    # ========================================================

    def build_sidebar(self):

        label = tk.Label(
            self.sidebar,
            text="ANALYSIS MODULES",
            bg="#202a35",
            fg="#95a5a6",
            font=("Segoe UI", 9, "bold")
        )

        label.pack(
            anchor="w",
            padx=20,
            pady=(25, 12)
        )

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("BET Analysis", self.show_bet),
            ("BJH Analysis", self.show_bjh),
            ("DFT Analysis", self.show_dft),
            ("EDS Analysis", self.show_eds),
            ("XRD / SRD", self.show_xrd),
            ("SEM / TEM", self.show_morphology),
            ("Reports", self.show_reports)
        ]

        for text, command in buttons:

            button = tk.Button(
                self.sidebar,
                text=text,
                command=command,
                anchor="w",
                bg="#202a35",
                fg="white",
                activebackground="#34495e",
                activeforeground="white",
                relief="flat",
                bd=0,
                font=("Segoe UI", 10),
                padx=20,
                pady=11,
                cursor="hand2"
            )

            button.pack(
                fill="x"
            )

    # ========================================================
    # CONTENT HELPERS
    # ========================================================

    def clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    def page_title(self, title, description):

        frame = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        frame.pack(
            fill="x",
            padx=30,
            pady=(25, 10)
        )

        tk.Label(
            frame,
            text=title,
            bg="#f4f6f8",
            fg="#17202a",
            font=("Segoe UI", 22, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            frame,
            text=description,
            bg="#f4f6f8",
            fg="#667085",
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

    def card(
        self,
        parent,
        title,
        value,
        subtitle=""
    ):

        frame = tk.Frame(
            parent,
            bg="white",
            bd=1,
            relief="solid"
        )

        tk.Label(
            frame,
            text=title,
            bg="white",
            fg="#667085",
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(16, 5)
        )

        tk.Label(
            frame,
            text=value,
            bg="white",
            fg="#17202a",
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w",
            padx=18
        )

        if subtitle:

            tk.Label(
                frame,
                text=subtitle,
                bg="white",
                fg="#98a2b3",
                font=("Segoe UI", 9)
            ).pack(
                anchor="w",
                padx=18,
                pady=(3, 15)
            )

        else:

            tk.Frame(
                frame,
                bg="white",
                height=15
            ).pack()

        return frame

    def action_button(
        self,
        parent,
        text,
        command
    ):

        return ttk.Button(
            parent,
            text=text,
            command=command
        )

    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):

        self.clear_content()

        self.page_title(
            "Characterization Dashboard",
            "Overview of the available MWCNT characterization datasets."
        )

        summary = analysis.get_characterization_summary()

        cards = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        cards.pack(
            fill="x",
            padx=30,
            pady=10
        )

        values = [
            (
                "BET Surface Area",
                summary["BET surface area (m²/g)"],
                "m²/g"
            ),
            (
                "BJH Mode Radius",
                summary[
                    "BJH adsorption mode radius (nm)"
                ],
                "adsorption"
            ),
            (
                "DFT Peak Width",
                summary[
                    "DFT peak pore width (nm)"
                ],
                "nm"
            ),
            (
                "EDS Composition",
                summary[
                    "EDS total weight (%)"
                ],
                "% total"
            ),
            (
                "SEM Images",
                summary["SEM image count"],
                "images"
            ),
            (
                "TEM Images",
                summary["TEM image count"],
                "images"
            )
        ]

        for index, (title, value, subtitle) in enumerate(values):

           

            display = (
                "N/A"
                if value is None
                else f"{value:.4f}"
                if isinstance(value, float)
                else str(value)
            )

            self.card(
                cards,
                title,
                display,
                subtitle
            ).grid(
                row=index // 3,
                column=index % 3,
                padx=6,
                pady=6,
                sticky="nsew"
            )

        for column in range(3):
            cards.columnconfigure(
                column,
                weight=1
            )

        evaluation_frame = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid"
        )

        evaluation_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        tk.Label(
            evaluation_frame,
            text="Characterization Status",
            bg="white",
            fg="#17202a",
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
        )

        statistics = analysis.get_dataset_statistics()

        tk.Label(
            evaluation_frame,
            text=(
                f"Processed datasets available: "
                f"{statistics['available']} / "
                f"{statistics['total']} "
                f"({statistics['percentage']:.1f}%)"
            ),
            bg="white",
            fg="#344054",
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            padx=20,
            pady=5
        )

        for item in analysis.evaluate_characterization():

            tk.Label(
                evaluation_frame,
                text="• " + item,
                bg="white",
                fg="#475467",
                font=("Segoe UI", 10),
                anchor="w"
            ).pack(
                fill="x",
                padx=25,
                pady=3
            )

    # ========================================================
    # BET
    # ========================================================

    def show_bet(self):

        self.clear_content()

        self.page_title(
            "BET Surface Area Analysis",
            "Nitrogen adsorption-desorption and specific surface area."
        )

        area = analysis.get_bet_surface_area()

        top = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        top.pack(
            fill="x",
            padx=30
        )

        value = (
            "N/A"
            if area is None
            else f"{area:.3f} m²/g"
        )

        self.card(
            top,
            "BET Surface Area",
            value,
            "Multi-point BET"
        ).pack(
            side="left",
            padx=(0, 10)
        )

        points = analysis.get_bet_isotherm_summary()

        self.card(
            top,
            "Isotherm Points",
            str(points["total_points"]),
            "adsorption + desorption"
        ).pack(
            side="left"
        )

        controls = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        controls.pack(
            fill="x",
            padx=30,
            pady=15
        )

        self.action_button(
            controls,
            "Generate BET Plot",
            self.generate_bet_plot
        ).pack(
            side="left"
        )

        table_frame = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        columns = (
            "parameter",
            "method",
            "value",
            "unit"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "parameter": "Parameter",
            "method": "Method",
            "value": "Value",
            "unit": "Unit"
        }

        for column in columns:

            tree.heading(
                column,
                text=headings[column]
            )

            tree.column(
                column,
                width=180
            )

        for row in analysis.get_bet_parameters():

            tree.insert(
                "",
                "end",
                values=(
                    row["parameter"],
                    row["method"],
                    row["value"],
                    row["unit"]
                )
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ========================================================
    # BJH
    # ========================================================

    def show_bjh(self):

        self.clear_content()

        self.page_title(
            "BJH Pore Size Analysis",
            "Separate adsorption and desorption pore-size distributions."
        )

        summary = analysis.get_bjh_summary()

        cards = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        cards.pack(
            fill="x",
            padx=30
        )

        card_data = [
            (
                "Adsorption Radius",
                summary["adsorption_mode_radius_nm"],
                "nm"
            ),
            (
                "Adsorption Diameter",
                summary["adsorption_mode_diameter_nm"],
                "nm"
            ),
            (
                "Adsorption Pore Volume",
                summary[
                    "adsorption_total_pore_volume_cm3_g"
                ],
                "cm³/g"
            ),
            (
                "Desorption Radius",
                summary["desorption_mode_radius_nm"],
                "nm"
            ),
            (
                "Desorption Diameter",
                summary["desorption_mode_diameter_nm"],
                "nm"
            ),
            (
                "Desorption Pore Volume",
                summary[
                    "desorption_total_pore_volume_cm3_g"
                ],
                "cm³/g"
            )
        ]

        for i, (title, value, unit) in enumerate(card_data):

            text = (
                "N/A"
                if value is None
                else f"{value:.4f}"
            )

            self.card(
                cards,
                title,
                text,
                unit
            ).grid(
                row=i // 3,
                column=i % 3,
                padx=6,
                pady=6,
                sticky="nsew"
            )

        for i in range(3):
            cards.columnconfigure(
                i,
                weight=1
            )

        buttons = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        buttons.pack(
            fill="x",
            padx=30,
            pady=15
        )

        self.action_button(
            buttons,
            "Adsorption Plot",
            self.generate_bjh_adsorption
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.action_button(
            buttons,
            "Desorption Plot",
            self.generate_bjh_desorption
        ).pack(
            side="left",
            padx=8
        )

        self.action_button(
            buttons,
            "Comparison Plot",
            self.generate_bjh_comparison
        ).pack(
            side="left",
            padx=8
        )

        note = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid"
        )

        note.pack(
            fill="x",
            padx=30,
            pady=10
        )

        tk.Label(
            note,
            text=(
                "BJH reporting distinguishes pore radius from pore diameter. "
                "The mode is obtained from the maximum dV/dlog(r) value "
                "in the selected distribution."
            ),
            bg="white",
            fg="#475467",
            font=("Segoe UI", 10),
            wraplength=1000,
            justify="left"
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

    # ========================================================
    # DFT
    # ========================================================

    def show_dft(self):

        self.clear_content()

        self.page_title(
            "DFT Pore Structure Analysis",
            "Pore-width distribution and model-fitting evaluation."
        )

        summary = analysis.get_dft_summary()
        fit = analysis.calculate_dft_fit_statistics()

        cards = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        cards.pack(
            fill="x",
            padx=30
        )

        data = [
            (
                "Peak Pore Width",
                summary["peak_pore_width_nm"],
                "nm"
            ),
            (
                "Peak Differential Volume",
                summary[
                    "peak_differential_volume_cm3_nm_g"
                ],
                "cm³/g/nm"
            ),
            (
                "Total Pore Volume",
                summary[
                    "total_pore_volume_cm3_g"
                ],
                "cm³/g"
            ),
            (
                "Surface Area",
                summary[
                    "total_surface_area_m2_g"
                ],
                "m²/g"
            ),
            (
                "Fit RMSE",
                fit["rmse"],
                "cm³/g"
            ),
            (
                "Fit R²",
                fit["r2"],
                "dimensionless"
            )
        ]

        for i, (title, value, unit) in enumerate(data):

            if value is None:
                text = "N/A"
            elif isinstance(value, float):
                text = f"{value:.5f}"
            else:
                text = str(value)

            self.card(
                cards,
                title,
                text,
                unit
            ).grid(
                row=i // 3,
                column=i % 3,
                padx=6,
                pady=6,
                sticky="nsew"
            )

        for i in range(3):
            cards.columnconfigure(
                i,
                weight=1
            )

        buttons = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        buttons.pack(
            fill="x",
            padx=30,
            pady=15
        )

        self.action_button(
            buttons,
            "Pore Distribution",
            self.generate_dft_distribution
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.action_button(
            buttons,
            "Surface Area Plot",
            self.generate_dft_surface
        ).pack(
            side="left",
            padx=8
        )

        self.action_button(
            buttons,
            "Fitting Plot",
            self.generate_dft_fitting
        ).pack(
            side="left",
            padx=8
        )

    # ========================================================
    # EDS
    # ========================================================

    def show_eds(self):

        self.clear_content()

        self.page_title(
            "EDS Elemental Analysis",
            "Elemental composition obtained from the processed EDS dataset."
        )

        summary = analysis.get_eds_summary()

        top = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        top.pack(
            fill="x",
            padx=30
        )

        self.card(
            top,
            "Total Composition",
            f"{summary['total_weight_percent']:.2f}%",
            "sum of detected elements"
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.card(
            top,
            "Detected Elements",
            str(summary["element_count"]),
            "elements"
        ).pack(
            side="left"
        )

        buttons = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        buttons.pack(
            fill="x",
            padx=30,
            pady=15
        )

        self.action_button(
            buttons,
            "Generate EDS Plot",
            self.generate_eds_plot
        ).pack(
            side="left"
        )

        frame = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        columns = (
            "element",
            "weight",
            "sigma"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        tree.heading(
            "element",
            text="Element"
        )

        tree.heading(
            "weight",
            text="Weight (%)"
        )

        tree.heading(
            "sigma",
            text="Sigma"
        )

        for item in summary["elements"]:

            tree.insert(
                "",
                "end",
                values=(
                    item["element"],
                    item["weight_percent"],
                    item["sigma"]
                )
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ========================================================
    # XRD
    # ========================================================

    def show_xrd(self):

        self.clear_content()

        self.page_title(
            "XRD / SRD Analysis",
            "Diffraction-pattern inspection and local peak detection."
        )

        summary = analysis.get_xrd_summary()

        strongest = summary["strongest_point"]

        if strongest:

            theta = strongest["two_theta"]
            intensity = strongest["intensity"]

        else:

            theta = None
            intensity = None

        top = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        top.pack(
            fill="x",
            padx=30
        )

        self.card(
            top,
            "Strongest Intensity Point",
            "N/A" if theta is None else f"{theta:.4f}°",
            "2θ"
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.card(
            top,
            "Intensity",
            "N/A" if intensity is None else f"{intensity:.0f}",
            "counts"
        ).pack(
            side="left",
            padx=10
        )

        self.card(
            top,
            "Detected Local Peaks",
            str(summary["detected_peak_count"]),
            "candidate peaks"
        ).pack(
            side="left",
            padx=10
        )

        buttons = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        buttons.pack(
            fill="x",
            padx=30,
            pady=15
        )

        self.action_button(
            buttons,
            "Generate XRD Plot",
            self.generate_xrd_plot
        ).pack(
            side="left"
        )

        frame = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        columns = (
            "theta",
            "intensity",
            "prominence"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        tree.heading(
            "theta",
            text="2θ (degrees)"
        )

        tree.heading(
            "intensity",
            text="Intensity"
        )

        tree.heading(
            "prominence",
            text="Prominence"
        )

        for peak in summary["detected_peaks"]:

            tree.insert(
                "",
                "end",
                values=(
                    f"{peak['two_theta']:.4f}",
                    f"{peak['intensity']:.0f}",
                    f"{peak['prominence']:.2f}"
                )
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ========================================================
    # SEM / TEM
    # ========================================================

    def show_morphology(self):

        self.clear_content()

        self.page_title(
            "SEM / TEM Morphology",
            "Available microscopy images and acquisition metadata."
        )

        images = analysis.get_image_paths()

        top = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        top.pack(
            fill="x",
            padx=30
        )

        self.card(
            top,
            "SEM Images",
            str(len(images["sem"])),
            "available"
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.card(
            top,
            "TEM Images",
            str(len(images["tem"])),
            "available"
        ).pack(
            side="left"
        )

        note = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid"
        )

        note.pack(
            fill="x",
            padx=30,
            pady=15
        )

        tk.Label(
            note,
            text=(
                "Important: this system records the available SEM/TEM images "
                "but does not invent CNT diameter, length, dispersion or "
                "morphological measurements. Quantitative image measurements "
                "should be obtained from properly calibrated images."
            ),
            bg="white",
            fg="#475467",
            font=("Segoe UI", 10),
            wraplength=1050,
            justify="left"
        ).pack(
            anchor="w",
            padx=20,
            pady=15
        )

        frame = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=5
        )

        columns = (
            "file",
            "magnification",
            "eht",
            "wd",
            "pixel"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "file": "Image",
            "magnification": "Magnification",
            "eht": "EHT",
            "wd": "Working Distance",
            "pixel": "Pixel Size"
        }

        for column in columns:

            tree.heading(
                column,
                text=headings[column]
            )

        for row in analysis.load_sem_metadata():

            tree.insert(
                "",
                "end",
                values=(
                    row.get("file", ""),
                    row.get("magnification", ""),
                    row.get("eht_kv", ""),
                    row.get("wd_mm", ""),
                    row.get("pixel_size_nm", "")
                )
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ========================================================
    # REPORTS
    # ========================================================

    def show_reports(self):

        self.clear_content()

        self.page_title(
            "Scientific Reports",
            "Generate and manage characterization reports."
        )

        controls = tk.Frame(
            self.content,
            bg="#f4f6f8"
        )

        controls.pack(
            fill="x",
            padx=30,
            pady=10
        )

        self.action_button(
            controls,
            "Generate Complete Report",
            self.generate_report
        ).pack(
            side="left"
        )

        frame = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=15
        )

        reports_list = database.get_reports()

        if not reports_list:

            tk.Label(
                frame,
                text="No reports have been generated yet.",
                bg="white",
                fg="#667085",
                font=("Segoe UI", 11)
            ).pack(
                pady=50
            )

            return

        columns = (
            "id",
            "filename",
            "created"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        tree.heading(
            "id",
            text="ID"
        )

        tree.heading(
            "filename",
            text="Report"
        )

        tree.heading(
            "created",
            text="Created"
        )

        for item in reports_list:

            tree.insert(
                "",
                "end",
                values=(
                    item.get("id", ""),
                    item.get("filename", ""),
                    item.get("created_at", "")
                )
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ========================================================
    # PLOT ACTIONS
    # ========================================================

    def notify_plot(self, function):

        try:

            path = function()

            messagebox.showinfo(
                "Plot Generated",
                f"Plot generated successfully:\n\n{path}"
            )

        except Exception as error:

            messagebox.showerror(
                "Plot Error",
                str(error)
            )

    def generate_bet_plot(self):
        self.notify_plot(
            visualization.plot_bet_isotherm
        )

    def generate_bjh_adsorption(self):
        self.notify_plot(
            visualization.plot_bjh_adsorption
        )

    def generate_bjh_desorption(self):
        self.notify_plot(
            visualization.plot_bjh_desorption
        )

    def generate_bjh_comparison(self):
        self.notify_plot(
            visualization.plot_bjh_comparison
        )

    def generate_dft_distribution(self):
        self.notify_plot(
            visualization.plot_dft_distribution
        )

    def generate_dft_surface(self):
        self.notify_plot(
            visualization.plot_dft_surface_area
        )

    def generate_dft_fitting(self):
        self.notify_plot(
            visualization.plot_dft_fitting
        )

    def generate_eds_plot(self):
        self.notify_plot(
            visualization.plot_eds_composition
        )

    def generate_xrd_plot(self):
        self.notify_plot(
            visualization.plot_xrd
        )

    # ========================================================
    # REPORT
    # ========================================================

    def generate_report(self):

        try:

            visualization.generate_all_plots()

            path = reports.generate_report()

            database.save_report(
                str(path)
            )

            database.save_analysis_history(
                "Complete characterization report generated"
            )

            messagebox.showinfo(
                "Report Generated",
                f"Report generated successfully:\n\n{path}"
            )

            self.show_reports()

        except Exception as error:

            messagebox.showerror(
                "Report Error",
                str(error)
            )


def run_application():

    app = MWCNTApplication()

    app.mainloop()


if __name__ == "__main__":
    run_application()