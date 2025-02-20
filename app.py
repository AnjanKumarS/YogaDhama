from flask import Flask, request, jsonify, render_template
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder="templates")

# ✅ Load dataset for Chatbot
file_path = r"C:\Users\anjan\OneDrive\Desktop\All_Mudras_Dataset.xlsx"
df = pd.read_excel(file_path)

df = df.applymap(lambda x: x.strip().lower() if isinstance(x, str) else x)

# Convert dataset into a dictionary for quick lookup using multiple keys
mudra_dict = {}
for _, row in df.iterrows():
    names = [
        row["Name"].strip().lower().replace(" ", ""),
        row["Sanskrit Name"].strip().lower().replace(" ", ""),
        row["Alternative Name"].strip().lower().replace(" ", "")
    ]
    for name in names:
        mudra_dict[name] = row.to_dict()

# ✅ Scraping Function for Hasta Mudras
def scrape_hasta_mudra():
    url = "https://www.fitsri.com/yoga-mudras#are-mudras-scientific"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: Unable to fetch the website. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")

    if not table:
        print("Error: Mudra table not found.")
        return None

    mudras = []
    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            mudra = {
                "sn": cols[0].text.strip(),
                "name": cols[1].text.strip(),
                "image": cols[2].find("img")["src"] if cols[2].find("img") else "",
                "description": cols[3].text.strip(),
                "benefits": cols[4].text.strip() if len(cols) > 4 else ""
            }
            mudras.append(mudra)

    return mudras

# ✅ Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/chat")
def chat():
    return render_template("index.html")

@app.route("/get_mudra", methods=["POST"])
def get_mudra():
    data = request.json
    user_input = data.get("mudra_name", "").strip().lower()
    is_voice = data.get("is_voice", False)
    
    user_input = re.sub(r"[^a-zA-Z0-9]", "", user_input)

    if user_input in mudra_dict:
        mudra_info = mudra_dict[user_input]
        response = {
            "status": "success",
            "sanskrit_name": mudra_info.get("Sanskrit Name", "N/A").title(),
            "alternative_name": mudra_info.get("Alternative Name", "N/A").title(),
            "type": mudra_info.get("Type of Mudra", "N/A").title(),
            "benefits": mudra_info.get("Benefits", "N/A"),
            "procedure": mudra_info.get("Procedure", "N/A"),
            "dos": mudra_info.get("Dos", "N/A"),
            "donts": mudra_info.get("Donts", "N/A"),
            "ordering": mudra_info.get("Ordering of Mudra", "N/A"),
            "cures": mudra_info.get("Disease it Cures", "N/A"),
            "time": mudra_info.get("Time", "N/A"),
            "frequency": mudra_info.get("Frequency of Doing", "N/A"),
            "is_voice": is_voice
        }
    else:
        response = {"status": "error", "message": "❌ Sorry, I don't know that mudra. Try another one!"}
    
    return jsonify(response)

@app.route("/hasta-mudra")
def hasta_mudra():
    mudras = scrape_hasta_mudra()
    if mudras:
        return render_template("hasta_mudra.html", mudras=mudras)
    else:
        return "Failed to scrape the page."

if __name__ == "__main__":
    app.run(debug=True)
