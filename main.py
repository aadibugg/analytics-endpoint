import os
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = "ak_cgsdusz7f3lpjqe8seo4yide"
MY_EMAIL = "your-email@example.com"  # <-- put YOUR login email here

# This runs on every response and adds the CORS headers the grader needs
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response

@app.route("/analytics", methods=["POST", "OPTIONS"])
def analytics():
    # Browsers send a "preflight" OPTIONS request before the real POST — just say OK
    if request.method == "OPTIONS":
        return "", 200

    # --- Step A: check the password ---
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # --- Step B: read the events ---
    data = request.get_json(force=True, silent=True) or {}
    events = data.get("events", [])

    # --- Step C: do the math ---
    total_events = len(events)

    unique_users = set()          # a set automatically ignores duplicates
    revenue = 0.0
    user_totals = {}              # dict: user -> total positive amount

    for e in events:
        user = e.get("user")
        amount = e.get("amount", 0)

        unique_users.add(user)

        if amount > 0:            # only count positive amounts
            revenue += amount
            user_totals[user] = user_totals.get(user, 0) + amount

    # find the user with the highest positive total
    top_user = max(user_totals, key=user_totals.get) if user_totals else None

    # --- Step D: send back the answer ---
    return jsonify({
        "email": MY_EMAIL,
        "total_events": total_events,
        "unique_users": len(unique_users),
        "revenue": round(revenue, 2),
        "top_user": top_user
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
