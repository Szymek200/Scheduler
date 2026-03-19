# 📅 AI Shift Scheduler - Workplace Management System

A desktop application built with **PySide6** designed for automatic scheduling and optimization of employee shifts across multiple locations. The system accounts for individual employee preferences, contract types (FTE), and specific workplace requirements.

## 🚀 Key Features

* **Automated Scheduling**: An algorithm that assigns employees to shifts based on availability, legal constraints, and site requirements.
* **Employee Management**: Database for tracking staff members, including their PESEL (ID) and employment contract details (e.g., 1.0, 0.5 FTE).
* **Workplace Requirements**: Define cyclic shifts (Morning/Afternoon) and specific needs for different locations.
* **Rule Engine**:
    * **Worker Rules**: Validates daily rest periods, maximum working hours, and prevents overlapping shifts.
    * **Cyclic Rules**: Establishes fixed time windows for specific workplaces.
* **Data Persistence**: Seamlessly save and load the entire database state using JSON serialization.
* **Responsive UI**: A GUI built with Qt Designer featuring a dynamic layout that scales with the window size.

## 🛠️ Tech Stack

* **Language**: Python 3.10+
* **GUI Framework**: PySide6 (Qt for Python)
* **Architecture**: Object-Oriented Design (Worker, Place, Shift, Rule classes)
* **Data Format**: JSON

## 📋 System Logic

The project utilizes a specialized shift-filtering logic:
1.  **OR Logic (Places)**: A workplace accepts an assignment if it matches *any* of the defined time-frame rules.
2.  **AND Logic (Workers)**: An employee can only take a shift if *all* legal and health-related rules (rest periods, hour limits) are satisfied.


