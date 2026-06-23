from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Storage recommendations based on crop type and conditions
STORAGE_DATA = {
    "wheat": {
        "hindi": "गेहूँ",
        "ideal_temp": "10-15°C",
        "ideal_humidity": "60-65%",
        "max_duration": "12-18 महीने",
        "moisture_limit": "12% से कम",
        "storage_type": "बोरी / साइलो / धातु की टंकी",
        "tips": [
            "गेहूँ को धूप में सुखाकर 12% नमी से कम करें",
            "साफ और सूखी बोरियों में भरें",
            "ज़मीन से ऊपर रखें, नमी से बचाएं",
            "हर महीने पलटाई करें"
        ],
        "warnings": [],
        "icon": "🌾"
    },
    "rice": {
        "hindi": "चावल / धान",
        "ideal_temp": "10-15°C",
        "ideal_humidity": "65-70%",
        "max_duration": "12 महीने",
        "moisture_limit": "14% से कम",
        "storage_type": "बोरी / सूखी कोठी",
        "tips": [
            "धान को अच्छी तरह सुखाएं",
            "हवादार जगह में रखें",
            "कीटनाशक पाउडर इस्तेमाल करें"
        ],
        "warnings": [],
        "icon": "🍚"
    },
    "corn": {
        "hindi": "मक्का",
        "ideal_temp": "10-15°C",
        "ideal_humidity": "60-65%",
        "max_duration": "6-12 महीने",
        "moisture_limit": "12% से कम",
        "storage_type": "बोरी / सूखी टंकी",
        "tips": [
            "अच्छी तरह सुखाएं — मक्का में जल्दी फफूंदी लगती है",
            "ठंडी और अंधेरी जगह रखें"
        ],
        "warnings": ["ज़्यादा नमी से aflatoxin का खतरा होता है!"],
        "icon": "🌽"
    },
    "potato": {
        "hindi": "आलू",
        "ideal_temp": "2-4°C",
        "ideal_humidity": "90-95%",
        "max_duration": "4-6 महीने",
        "moisture_limit": "लागू नहीं",
        "storage_type": "शीतगृह (Cold Storage)",
        "tips": [
            "शीतगृह में रखना अनिवार्य है",
            "हरे या अंकुरित आलू न रखें",
            "प्रकाश से दूर रखें"
        ],
        "warnings": ["बिना शीतगृह के 1-2 हफ्ते से ज़्यादा नहीं टिकता!"],
        "icon": "🥔"
    },
    "onion": {
        "hindi": "प्याज़",
        "ideal_temp": "0-5°C या 25-30°C",
        "ideal_humidity": "65-70%",
        "max_duration": "3-6 महीने",
        "moisture_limit": "लागू नहीं",
        "storage_type": "जालीदार टोकरी / हवादार कमरा",
        "tips": [
            "हवा आने-जाने वाली जगह में रखें",
            "गीले या सड़े प्याज़ अलग करें",
            "ज़मीन पर ढेर न लगाएं"
        ],
        "warnings": [],
        "icon": "🧅"
    },
    "soybean": {
        "hindi": "सोयाबीन",
        "ideal_temp": "10-15°C",
        "ideal_humidity": "60-65%",
        "max_duration": "12 महीने",
        "moisture_limit": "12% से कम",
        "storage_type": "बोरी / साइलो",
        "tips": [
            "नमी 12% से कम होनी चाहिए",
            "धूप में सुखाकर रखें",
            "कीड़ों से बचाने के लिए दवाई डालें"
        ],
        "warnings": [],
        "icon": "🫘"
    },
    "mustard": {
        "hindi": "सरसों",
        "ideal_temp": "10-15°C",
        "ideal_humidity": "55-60%",
        "max_duration": "12-18 महीने",
        "moisture_limit": "8% से कम",
        "storage_type": "सूखी बोरी / टंकी",
        "tips": [
            "बहुत सूखा रखें — तेल बीज जल्दी खराब होते हैं",
            "ठंडी और अंधेरी जगह रखें"
        ],
        "warnings": [],
        "icon": "🌿"
    },
    "sugarcane": {
        "hindi": "गन्ना",
        "ideal_temp": "0-2°C",
        "ideal_humidity": "90-95%",
        "max_duration": "2-4 हफ्ते",
        "moisture_limit": "लागू नहीं",
        "storage_type": "खेत में / शीतगृह",
        "tips": [
            "काटने के बाद जल्द से जल्द पेराई करें",
            "लंबे समय तक नहीं रखा जा सकता"
        ],
        "warnings": ["कटाई के बाद 24-48 घंटे में पेराई ज़रूरी!"],
        "icon": "🎋"
    }
}


def analyze_conditions(crop, temp, humidity, moisture, duration):
    """Analyze farmer's conditions and give personalized advice."""
    data = STORAGE_DATA.get(crop)
    if not data:
        return None

    issues = []
    suggestions = []
    risk_level = "कम जोखिम ✅"

    # Parse ideal ranges
    ideal_temp_str = data["ideal_temp"]
    ideal_humidity_str = data["ideal_humidity"]

    # Temperature check
    try:
        temp_parts = ideal_temp_str.replace("°C", "").split("-")
        t_min, t_max = float(temp_parts[0]), float(temp_parts[1])
        if temp < t_min:
            suggestions.append(f"तापमान ({temp}°C) थोड़ा कम है। आदर्श: {ideal_temp_str}")
        elif temp > t_max + 5:
            issues.append(f"तापमान ({temp}°C) बहुत अधिक है! यह फसल खराब कर सकता है।")
            risk_level = "उच्च जोखिम ⚠️"
        elif temp > t_max:
            suggestions.append(f"तापमान ({temp}°C) थोड़ा अधिक है। आदर्श: {ideal_temp_str}")
    except:
        pass

    # Humidity check
    try:
        hum_parts = ideal_humidity_str.replace("%", "").split("-")
        h_min, h_max = float(hum_parts[0]), float(hum_parts[1])
        if humidity > h_max + 10:
            issues.append(f"नमी ({humidity}%) बहुत ज़्यादा है! फफूंदी और सड़न का खतरा।")
            risk_level = "उच्च जोखिम ⚠️"
        elif humidity > h_max:
            suggestions.append(f"नमी ({humidity}%) थोड़ी अधिक है। आदर्श: {ideal_humidity_str}")
        elif humidity < h_min - 10:
            suggestions.append(f"नमी ({humidity}%) कम है। कुछ फसलों में सूखापन आ सकता है।")
    except:
        pass

    # Moisture check
    if "%" in data["moisture_limit"] and moisture > 0:
        try:
            limit = float(data["moisture_limit"].replace("%", "").replace("से कम", "").strip())
            if moisture > limit:
                issues.append(f"अनाज की नमी ({moisture}%) सीमा से अधिक है! तुरंत सुखाएं।")
                risk_level = "उच्च जोखिम ⚠️"
        except:
            pass

    if not issues and not suggestions:
        suggestions.append("आपकी भंडारण स्थिति अच्छी है!")

    return {
        "issues": issues,
        "suggestions": suggestions,
        "risk_level": risk_level
    }


@app.route("/")
def index():
    crops = {k: {"hindi": v["hindi"], "icon": v["icon"]} for k, v in STORAGE_DATA.items()}
    return render_template("index.html", crops=crops)


@app.route("/get_recommendation", methods=["POST"])
def get_recommendation():
    data = request.get_json()
    crop = data.get("crop")
    temp = float(data.get("temp", 25))
    humidity = float(data.get("humidity", 70))
    moisture = float(data.get("moisture", 0))
    duration = data.get("duration", "")

    crop_data = STORAGE_DATA.get(crop)
    if not crop_data:
        return jsonify({"error": "फसल नहीं मिली"}), 404

    analysis = analyze_conditions(crop, temp, humidity, moisture, duration)

    return jsonify({
        "crop_data": crop_data,
        "analysis": analysis
    })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)