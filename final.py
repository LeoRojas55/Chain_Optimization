import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def simulate_markov_chain_live():
    try:
        days = int(entry_days.get())
        num_products = int(entry_products.get())
        total_price = float(entry_price.get())

        if days <= 0 or num_products <= 0 or total_price <= 0:
            raise ValueError("Los valores deben ser mayores a cero.")

        transition_matrix = np.array([
            [0.6, 0.3, 0.05, 0.03, 0.02],
            [0.2, 0.5, 0.15, 0.1, 0.05],
            [0.1, 0.2, 0.5, 0.15, 0.05],
            [0.05, 0.1, 0.2, 0.5, 0.15],
            [0.02, 0.05, 0.1, 0.2, 0.63]
        ])

        states = np.zeros((days, num_products), dtype=int)
        states[0, :] = 0

        penalties = [1.0, 0.95, 0.85, 0.5, 0.3]
        cost_per_day = total_price / days
        total_cost = 0
        discounts = [0] * 5

        new_window = tk.Toplevel(root)
        new_window.title("Simulación en Tiempo Real")
        fig, ax = plt.subplots(figsize=(8, 5))
        canvas = FigureCanvasTkAgg(fig, master=new_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()

        x_data = []
        y_data = [[] for _ in range(5)]
        state_names = ['Excelente', 'Bueno', 'Regular', 'Defectuoso', 'Malo']

        def update_chart(t=0):
            nonlocal total_cost
            if t < days and new_window.winfo_exists():
                if t > 0:
                    for i in range(num_products):
                        current_state = states[t-1, i]
                        new_state = np.random.choice([0, 1, 2, 3, 4], p=transition_matrix[current_state])
                        states[t, i] = new_state

                counts = [np.sum(states[t] == i) for i in range(5)]
                daily_penalty = sum(counts[i] * penalties[i] * cost_per_day / num_products for i in range(5))

                for i in range(5):
                    discounts[i] += (counts[i] * (1 - penalties[i]) * cost_per_day / num_products)

                total_cost += daily_penalty

                x_data.append(t)
                for i in range(5):
                    y_data[i].append(counts[i])

                ax.clear()
                for i in range(5):
                    ax.plot(x_data, y_data[i], label=f"{state_names[i]} (n={counts[i]})", marker='o')
                ax.set_xlabel('Tiempo (días)')
                ax.set_ylabel('Número de productos')
                ax.set_title(f'Distribución de Estados en Tiempo Real\nCostos acumulados: ${total_cost:.2f} COP')
                ax.legend()
                ax.grid(True)
                canvas.draw()

                new_window.after(1000, lambda: update_chart(t+1))
            else:
                show_final_summary()

        def show_final_summary():
            final_counts = [np.sum(states[-1] == i) for i in range(5)]

            # Ventana con resumen y gráfica de barras apiladas
            summary_window = tk.Toplevel(new_window)
            summary_window.title("Resumen Final")

            # Gráfico de barras apiladas
            fig_summary, ax_summary = plt.subplots(figsize=(6, 4))
            ax_summary.barh(state_names, final_counts, color=plt.cm.tab20c.colors, edgecolor="black")
            ax_summary.set_xlabel("Cantidad")
            ax_summary.set_title("Distribución Final de Estados")
            ax_summary.grid(True, axis='x', linestyle='--', alpha=0.7)

            canvas_summary = FigureCanvasTkAgg(fig_summary, master=summary_window)
            canvas_summary.get_tk_widget().pack()

            # Texto del resumen
            summary_text = "Resumen Final:\n"
            for i in range(5):
                summary_text += (f"- {state_names[i]}: {final_counts[i]} productos "
                                 f"({final_counts[i] / num_products:.1%})\n"
                                 f"  Descuento acumulado: ${discounts[i]:.2f}\n")

            summary_label = tk.Label(summary_window, text=summary_text, justify=tk.LEFT, font=("Arial", 12))
            summary_label.pack(pady=10)

            # Nueva ventana para el gráfico de columnas apiladas
            stacked_window = tk.Toplevel(new_window)
            stacked_window.title("Gráfico de Columnas Apiladas")

            selected_days = np.linspace(0, days-1, 5, dtype=int)
            x_labels = [f"Día {d+1}" for d in selected_days]
            y_data_stacked = [np.sum(states[selected_days] == i, axis=1) for i in range(5)]

            fig_stacked, ax_stacked = plt.subplots(figsize=(8, 5))
            width = 0.7
            bottom_values = np.zeros(5)
            colors = plt.cm.tab20c.colors[:5]

            for i in range(5):
                ax_stacked.bar(x_labels, y_data_stacked[i], width, label=state_names[i], bottom=bottom_values, color=colors[i])
                bottom_values += y_data_stacked[i]

            ax_stacked.set_xlabel("Días")
            ax_stacked.set_ylabel("Cantidad de productos")
            ax_stacked.set_title("Distribución de Estados (Columnas Apiladas)")
            ax_stacked.legend()
            ax_stacked.grid(True, axis='y', linestyle='--', alpha=0.7)

            canvas_stacked = FigureCanvasTkAgg(fig_stacked, master=stacked_window)
            canvas_stacked.get_tk_widget().pack()

        update_chart()

    except ValueError as e:
        messagebox.showerror("Error de entrada", str(e))

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Simulación de Cadenas de Manufactura")
root.geometry("400x350")
root.configure(bg="#f0f0f0")

label_title = tk.Label(root, text="Optimización de Cadenas de Manufactura", font=("Arial", 14, "bold"), bg="#f0f0f0")
label_title.pack(pady=10)

frame_input = ttk.Frame(root)
frame_input.pack(pady=20)

label_days = ttk.Label(frame_input, text="Número de días:")
label_days.grid(row=0, column=0, padx=10, pady=10)
entry_days = ttk.Entry(frame_input, width=10)
entry_days.grid(row=0, column=1)

label_products = ttk.Label(frame_input, text="Número de productos:")
label_products.grid(row=1, column=0, padx=10, pady=10)
entry_products = ttk.Entry(frame_input, width=10)
entry_products.grid(row=1, column=1)

label_price = ttk.Label(frame_input, text="Precio total (COP):")
label_price.grid(row=2, column=0, padx=10, pady=10)
entry_price = ttk.Entry(frame_input, width=10)
entry_price.grid(row=2, column=1)

button_simulate = ttk.Button(root, text="Iniciar Simulación", command=simulate_markov_chain_live)
button_simulate.pack(pady=20)

root.mainloop()
