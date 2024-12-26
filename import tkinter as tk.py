import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt

class JobSchedulerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Job Scheduler")
        
        self.setup_process_input_section()
        self.setup_algorithm_selection()
        self.setup_results_section()

    def setup_process_input_section(self):
        self.process_frame = ttk.LabelFrame(self.master, text="Process Input")
        self.process_frame.grid(row=0, column=0, padx=10, pady=10)

        self.num_processes_label = ttk.Label(self.process_frame, text="Number of Processes:")
        self.num_processes_label.grid(row=0, column=0)
        
        self.num_processes = tk.IntVar(value=1)
        self.num_processes_spinbox = ttk.Spinbox(self.process_frame, from_=1, to=10, textvariable=self.num_processes, command=self.create_process_inputs)
        self.num_processes_spinbox.grid(row=0, column=1)

        self.process_inputs = []
        self.create_process_inputs()

    def create_process_inputs(self):
        for widget in self.process_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.destroy()
        
        self.process_inputs.clear()
        for i in range(self.num_processes.get()):
            ttk.Label(self.process_frame, text=f"Process {i+1}").grid(row=i+1, column=0)
            arrival_time = ttk.Entry(self.process_frame)
            arrival_time.grid(row=i+1, column=1)
            burst_time = ttk.Entry(self.process_frame)
            burst_time.grid(row=i+1, column=2)
            priority = ttk.Entry(self.process_frame)
            priority.grid(row=i+1, column=3)
            self.process_inputs.append((arrival_time, burst_time, priority))

        # Add labels for the input fields
        ttk.Label(self.process_frame, text="Arrival Time").grid(row=0, column=1)
        ttk.Label(self.process_frame, text="Burst Time").grid(row=0, column=2)
        ttk.Label(self.process_frame, text="Priority").grid(row=0, column=3)

    def setup_algorithm_selection(self):
        self.algorithm_frame = ttk.LabelFrame(self.master, text="Select Scheduling Algorithm")
        self.algorithm_frame.grid(row=1, column=0, padx=10, pady=10)

        self.algorithm_label = ttk.Label(self.algorithm_frame, text="Algorithm:")
        self.algorithm_label.grid(row=0, column=0)

        self.algorithm_var = tk.StringVar()
        self.algorithm_combobox = ttk.Combobox(self.algorithm_frame, textvariable=self.algorithm_var)
        self.algorithm_combobox['values'] = ["FCFS", "SJF", "SRTF", "RR", "Priority Non-Preemptive", "Priority Preemptive"]
        self.algorithm_combobox.grid(row=0, column=1)

        self.calculate_button = ttk.Button(self.algorithm_frame, text="Calculate Schedule", command=self.calculate_schedule)
        self.calculate_button.grid(row=0, column=2)

    def setup_results_section(self):
        self.results_frame = ttk.LabelFrame(self.master, text="Results")
        self.results_frame.grid(row=2, column=0, padx=10, pady=10)

        self.results_text = tk.Text(self.results_frame, width=50, height=10)
        self.results_text.grid(row=0, column=0)

    def calculate_schedule(self):
        try:
            processes = self.parse_process_inputs()
            algorithm = self.algorithm_var.get()
            if algorithm == "FCFS":
                schedule = self.fcfs_scheduling(processes)
            elif algorithm == "SJF":
                schedule = self.sjf_scheduling(processes)
            elif algorithm == "SRTF":
                schedule = self.srtf_scheduling(processes)
            elif algorithm == "RR":
                schedule = self.round_robin_scheduling(processes, quantum=2)  # Example quantum
            elif algorithm == "Priority Non-Preemptive":
                schedule = self.priority_non_preemptive(processes)
            elif algorithm == "Priority Preemptive":
                schedule = self.priority_preemptive(processes)
            else:
                raise ValueError("Invalid scheduling algorithm selected.")
            self.display_results(schedule)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def parse_process_inputs(self):
        processes = []
        for arrival_time, burst_time, priority in self.process_inputs:
            arrival = int(arrival_time.get())
            burst = int(burst_time.get())
            prio = int(priority.get())
            processes.append((arrival, burst, prio))
        return processes

    def display_results(self, schedule):
        self.results_text.delete(1.0, tk.END)  # Clear previous results
        for process in schedule:
            self.results_text.insert(tk.END, f"Process: {process['id']}, Start: {process['start']}, End: {process['end']}\n")
        self.create_gantt_chart(schedule)

    def create_gantt_chart(self, schedule):
        plt.figure(figsize=(10, 5))
        for process in schedule:
            plt.barh(process['id'], process['end'] - process['start'], left=process['start'])
        plt.xlabel('Time')
        plt.ylabel('Processes')
        plt.title('Gantt Chart')
        plt.show()

    # Scheduling Algorithms
    def fcfs_scheduling(self, processes):
        processes.sort(key=lambda x: x[0])  # Sort by arrival time
        schedule = []
        current_time = 0
        for i, (arrival, burst, priority) in enumerate(processes):
            if current_time < arrival:
                current_time = arrival
            start_time = current_time
            end_time = start_time + burst
            schedule.append({'id': f'P{i+1}', 'start': start_time, 'end': end_time})
            current_time = end_time
        return schedule

    def sjf_scheduling(self, processes):
        processes.sort(key=lambda x: (x[0], x[1]))  # Sort by arrival time and burst time
        schedule = []
        current_time = 0
        while processes:
            available_processes = [p for p in processes if p[0] <= current_time]
            if not available_processes:
                current_time = processes[0][0]  # Jump to next process arrival
                continue
            shortest_process = min(available_processes, key=lambda x: x[1])  # Select shortest job
            processes.remove(shortest_process)
            start_time = current_time
            end_time = start_time + shortest_process[1]
            schedule.append({'id': f'P{processes.index(shortest_process)+1}', 'start': start_time, 'end': end_time})
            current_time = end_time
        return schedule

    def srtf_scheduling(self, processes):
        # Shortest Remaining Time First implementation
        processes.sort(key=lambda x: x[0])  # Sort by arrival time
        schedule = []
        current_time = 0
        while processes:
            available_processes = [p for p in processes if p[0] <= current_time]
            if not available_processes:
                current_time = processes[0][0]  # Jump to next process arrival
                continue
            
            # Select the process with the shortest remaining time
            shortest_process = min(available_processes, key=lambda x: x[1])
            arrival, burst, priority = shortest_process
            processes.remove(shortest_process)
            start_time = current_time
            end_time = start_time + burst
            schedule.append({'id': f'P{processes.index(shortest_process)+1}', 'start': start_time, 'end': end_time})
            current_time = end_time
        return schedule

    def round_robin_scheduling(self, processes, quantum):
        queue = processes.copy()
        schedule = []
        current_time = 0
        while queue:
            process = queue.pop(0)
            arrival, burst, priority = process
            if current_time < arrival:
                current_time = arrival  # Wait for the process to arrive
            if burst > quantum:
                start_time = current_time
                end_time = start_time + quantum
                schedule.append({'id': f'P{processes.index(process)+1}', 'start': start_time, 'end': end_time})
                current_time = end_time
                queue.append((arrival, burst - quantum, priority))  # Re-add process with remaining burst time
            else:
                start_time = current_time
                end_time = start_time + burst
                schedule.append({'id': f'P{processes.index(process)+1}', 'start': start_time, 'end': end_time})
                current_time = end_time
        return schedule

    def priority_non_preemptive(self, processes):
        processes.sort(key=lambda x: (x[0], x[2]))  # Sort by arrival time and priority
        schedule = []
        current_time = 0
        while processes:
            available_processes = [p for p in processes if p[0] <= current_time]
            if not available_processes:
                current_time = processes[0][0]  # Jump to next process arrival
                continue
            highest_priority_process = min(available_processes, key=lambda x: x[2])  # Select highest priority
            processes.remove(highest_priority_process)
            arrival, burst, priority = highest_priority_process
            start_time = current_time
            end_time = start_time + burst
            schedule.append({'id': f'P{processes.index(highest_priority_process)+1}', 'start': start_time, 'end': end_time})
            current_time = end_time
        return schedule

    def priority_preemptive(self, processes):
        # Preemptive Priority Scheduling implementation
        processes.sort(key=lambda x: x[0])  # Sort by arrival time
        schedule = []
        current_time = 0
        while processes:
            available_processes = [p for p in processes if p[0] <= current_time]
            if not available_processes:
                current_time = processes[0][0]  # Jump to next process arrival
                continue
            
            # Select the process with the highest priority (lowest number)
            highest_priority_process = min(available_processes, key=lambda x: x[2])
            arrival, burst, priority = highest_priority_process
            
            if burst > 1:
                # Process will run for 1 time unit
                start_time = current_time
                end_time = start_time + 1
                schedule.append({'id': f'P{processes.index(highest_priority_process)+1}', 'start': start_time, 'end': end_time})
                current_time += 1
                # Update the burst time and re-add to the list
                processes.remove(highest_priority_process)
                processes.append((arrival, burst - 1, priority))
            else:
                # Process will finish
                start_time = current_time
                end_time = start_time + burst
                schedule.append({'id': f'P{processes.index(highest_priority_process)+1}', 'start': start_time, 'end': end_time})
                current_time = end_time
                processes.remove(highest_priority_process)
        return schedule

def main():
    root = tk.Tk()
    app = JobSchedulerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()