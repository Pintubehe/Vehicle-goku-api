from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

COPYRIGHT_STRING = "@gokuuuu_1"

DESIRED_ORDER = [
    "Owner Name", "Father's Name", "Owner Serial No", "Model Name", "Maker Model",
    "Vehicle Class", "Fuel Type", "Fuel Norms", "Registration Date", "Insurance Company",
    "Insurance No", "Insurance Expiry", "Insurance Upto", "Fitness Upto", "Tax Upto",
    "PUC No", "PUC Upto", "Financier Name", "Registered RTO",
    "Address", "City Name", "Phone"
]

def get_vehicle_details(rc_number: str) -> dict:
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile Safari/537.36)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        return {"error": str(e)}

    def get_value(label):
        try:
            div = soup.find("span", string=label).find_parent("div")
            return div.find("p").get_text(strip=True)
        except:
            return None

    def get_address():
        try:
            div = soup.find("span", string="Address").find_parent("div")
            addr = div.find("p").get_text(strip=True)
            if addr and len(addr) > 2:
                return addr
        except:
            pass

        try:
            span = soup.find("span", text=lambda x: x and "Address" in x)
            if span:
                addr = span.find_next("p").get_text(strip=True)
                if addr:
                    return addr
        except:
            pass

        try:
            blocks = soup.find_all("p")
            for b in blocks:
                text = b.get_text(strip=True)
                if any(word in text.lower() for word in ["road", "street", "colony", "nagar", "district", "house", "lane"]):
                    if len(text) > 5:
                        return text
        except:
            pass

        return None

    data = {key: get_value(key) for key in DESIRED_ORDER}
    data["Address"] = get_address()

    return data


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "🚗 Vehicle Info API with Address is running!",
        "developer": COPYRIGHT_STRING
    })


@app.route("/lookup", methods=["GET"])
def lookup_vehicle():
    rc_number = request.args.get("rc")
    if not rc_number:
        return jsonify({"error": "Please provide ?rc= parameter"}), 400

    details = get_vehicle_details(rc_number)

    ordered_details = OrderedDict()
    for key in DESIRED_ORDER:
        ordered_details[key] = details.get(key)

    ordered_details["copyright"] = COPYRIGHT_STRING
    return jsonify(ordered_details)


def handler(request):
    with app.app_context():
        return app.full_dispatch_request()