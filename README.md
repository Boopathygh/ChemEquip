Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop App)

A hybrid application that runs as both a Web Application and a Desktop Application to visualize and analyze chemical equipment parameters from CSV files.

This project uses a common Django REST backend that is consumed by both React (Web) and PyQt5 (Desktop) frontends.

Features

Upload CSV files containing chemical equipment data

Automatic data analysis using Pandas

Summary statistics (count, averages)

Equipment type distribution

Interactive charts (Chart.js for Web, Matplotlib for Desktop)

History of last 5 uploaded datasets

PDF report generation

Basic authentication

Hybrid architecture (Web + Desktop)

Tech Stack
Layer	Technology
Backend	Django + Django REST Framework
Data Processing	Pandas
Database	SQLite
Web Frontend	React.js + Chart.js
Desktop Frontend	PyQt5 + Matplotlib
Version Control	Git & GitHub
