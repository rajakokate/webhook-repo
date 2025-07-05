### Webhook Integration Assignment
## Overview
This project demonstrates how to:

Receive GitHub webhook events (push, pull request, merge)

Store them in MongoDB

Display them on a React frontend with updates every 15 seconds

## Repositories
action-repo: Repository where push, PR, merge events are triggered

webhook-repo: Flask backend with MongoDB to capture and store events

## Tech Stack
Backend: Flask + MongoDB Atlas

Frontend: React

Tunnel: Ngrok (for receiving GitHub webhooks)

# How It Works
Event Handling
Action	Format Logged
Push	{author} pushed to {to_branch} on {timestamp}
Pull Request	{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}
Merge	{author} merged branch {from_branch} to {to_branch} on {timestamp}

## Setup Instructions
# Prerequisites
Node.js & npm

Python 3 & pip

MongoDB Atlas cluster

Ngrok account

11.  Backend (Flask + MongoDB)

cd webhook-repo/backend
Add your MongoDB connection string in MONGO_URL (.env file to be created)
pip install -r requirements.txt
python app.py


Flask will start at http://localhost:5000

2️⃣ Expose Flask App with Ngrok

ngrok http 5000
Copy the HTTPS Forwarding URL like https://abcd-1234.ngrok-free.app

3️⃣ GitHub Webhook Setup
Go to your action-repo → Settings → Webhooks → Add Webhook:

Payload URL: https://your-ngrok-url/webhook

Content type: application/json

Events: Send me everything (recommended for demo)

Save

4️⃣ Frontend (React)

cd webhook-repo/frontend
npm install
npm start