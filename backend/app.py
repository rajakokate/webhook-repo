from flask import Flask, request , jsonify
from dotenv import load_dotenv
import os
from flask_cors import CORS
from pymongo import MongoClient
from dateutil import parser
from datetime import datetime
import pytz

load_dotenv()

#fetch URL from .env
mongo_url = os.getenv("MONGO_URL")

app = Flask(__name__)
CORS(app)

#This first URL has DNS issue
# MONGO_URI = "mongodb+srv://rajakokate:vaPtkdtl3syWTWFo@cluster0.yh1ip.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# MONGO_URI = "mongodb://rajakokate:vaPtkdtl3syWTWFo@cluster0-shard-00-00.yh1ip.mongodb.net:27017,cluster0-shard-00-01.yh1ip.mongodb.net:27017,cluster0-shard-00-02.yh1ip.mongodb.net:27017/?ssl=true&replicaSet=atlas-duwtzl-shard-0&authSource=admin&retryWrites=true&w=majority"


# Mongodb connection
client = MongoClient(mongo_url)
db = client['webhook-db'] #database
collection = db["webhook_events"] #collection


# Utility function to convert UTC to IST
def utc_to_ist(utc_str):
    try:
       #dateutil to handle both Z and +5:30 time format
       dt = parser.parse(utc_str)
       #convert to IST
       ist = dt.astimezone(pytz.timezone("Asia/Kolkata"))
       # returning IST format
       return ist.strftime("%d-%m-%Y %H:%M:%S %p")
    except Exception as e:
        print("TimeStamp converion failed:", e)
        return utc_str

#main route
@app.route('/webhook', methods=['POST'])
def github_webhook():

    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("Error parsing json", e)
        return jsonify({"error": "Invalid JSON"}), 400

    # Check pull_reqeuest
    if "pull_request" in data:
        pr_data = data ["pull_request"]
        action_type = data.get("action")

        #check if it is closed pull request
        if action_type =='closed' and pr_data.get('merged') is True:
            #MERGE
            event_type ="MERGE"
            request_id = str(pr_data.get('id'))
            author =  pr_data.get("user",{}).get("login")
            from_branch = pr_data.get('head', {}).get("ref")
            to_branch = pr_data.get("base", {}).get('ref')
            timestamp = pr_data.get("merged_at")
            timestamp = utc_to_ist(timestamp)

        # checks for PR raise
        else:
        #PULL_REQUEST
            event_type = "PULL_REQUEST"
            request_id = str(pr_data.get("id"))
            author = pr_data.get("user", {}).get('login')
            from_branch = pr_data.get("head", {}).get("ref")
            to_branch = pr_data.get("base",{}).get('ref')
            timestamp = pr_data.get("created_at")
            print("PUll request timestamp", timestamp)
            timestamp = utc_to_ist(timestamp)

        formatted_data = {
            "request_id": request_id,
            "author": author,
            "action": event_type,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }

        collection.insert_one(formatted_data)
        print(f"Saved clean {event_type} data", formatted_data)
        return jsonify({"Status":f"{event_type} event stored"}), 200
    
    # Handle push operation
    elif 'pusher' in data:
        event_type = 'PUSH'
        request_id = data.get("head_commit", {}).get("id")
        author =  data.get('pusher',{}).get("name")
        ref = data.get("ref")
        to_branch = ref.split("/")[-1] if ref else None
        from_branch = None  
        timestamp = data.get("head_commit", {}).get("timestamp")
        print('RAW timestamp from github:', timestamp)
        timestamp = utc_to_ist(timestamp)

        formatted_data = {
            "request_id" : request_id,
            "author": author,
            "action" : event_type,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }

        
        #Insert raw data into MongoDB
        collection.insert_one(formatted_data)
        print("saved push data", formatted_data)

        return jsonify({"status": "Push event stored"}), 200
    return jsonify({"message": "Unhandled event type"}), 200

# route for webhook logs
@app.route('/logs', methods=['GET'])
def get_logs():
    #Fetch all documents from collection and show newest first
    logs = collection.find().sort("timestamp", -1)

    result = []
    for log in logs:
        result.append ({
            "request_id":log.get("request_id"),
            "author": log.get('author'),
            "action": log.get("action"),
            "from_branch": log.get("from_branch"),
            "to_branch": log.get("to_branch"),
            "timestamp": log.get("timestamp")   
        })
    return jsonify(result),200

# Route to delete all logs from MondoDB, for testing purpose only
@app.route('/delete-logs', methods=['DELETE'])
def delete_logs():
    result = collection.delete_many({})
    return jsonify({"status": "deleted","deleted_count": result.deleted_count})

if __name__ == "__main__":
    app.run(debug=True)

