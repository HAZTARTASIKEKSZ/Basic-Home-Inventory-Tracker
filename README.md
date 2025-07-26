Basic Home Inventory Tracker
🧺 A simple Tkinter GUI app for managing two pantry inventories with real-time Google Sheets sync.

📝 Overview
Basic Home Inventory Tracker is a lightweight Python desktop application built with Tkinter. It allows you to add, subtract, search, and synchronize items in Google Sheets:

The app provides a clean GUI and seamless Google Sheets integration using a Google Service Account.

✨ Features
➕ Add or ➖ subtract item quantities with units (e.g., carrot 3 kg)

🔍 Search for items in the active inventory

🔄 Sync changes to Google Sheets and sort items alphabetically

🔁 Switch between two predefined sheets: "SHEET1" and "SHEET2"

🖼️ Clean and minimal Tkinter-based interface

🔐 Uses Google Service Account authentication for secure access

🚀 Getting Started
✅ Prerequisites
Make sure you have the following installed and ready:

Python 3.6 or higher
pip
Google Service Account JSON key file
A Google Sheets document !has to be connected to Google Service Account

🛠️ Installation
Clone the repository
git clone https://github.com/yourusername/Basic-Home-Inventory-Tracker.git
cd Basic-Home-Inventory-Tracker

Set up your Google Service Account

Place your JSON key file in the project folder.
Update the filename in the code (e.g., in app.py or elsoGUI.py) — modify the keyfile_path variable.
Configure the spreadsheet
Replace the placeholder SPREADSHEET_ID in your code with the actual ID of your Google Sheet.

📄 Setting Up Google Sheets API
Create a project on Google Cloud Console.

Enable the Google Sheets API and Google Drive API.

Create a Service Account and download the credentials as a JSON file.

Share your spreadsheet with the Service Account email (found in the JSON file), granting Editor access.

▶️ Running the Application
Launch the GUI with:
python app.py

You can now:

Add or subtract items
Search your inventory
Sync with Google Sheets

🧪 Usage Example
Add item: Type apple 2 kg in the "Elem hozzáadása" field and click the button.

Subtract item: Type apple 1 kg in the "Elem levonása" field and click the button.

Search: Use the search bar to find an item.

Sync: Click "Szinkronizálás" to push updates to Google Sheets and sort the inventory.

📁 Project Structure
graphql
Másolás
Szerkesztés
Basic-Home-Inventory-Tracker/
│
├── app.py                     # Main application script
├── requirements.txt           # Required Python packages
├── LICENSE                    # License file
├── README.md                  # This documentation file
└── your_service_account_key.json   # Google API credentials

