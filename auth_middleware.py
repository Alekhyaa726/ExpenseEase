from functools import wraps
import jwt
from flask import request, abort, current_app
from pymongo import MongoClient

uri = "mongodb+srv://ciyala:kXDUh8LovKrC3H8P@cluster0.pr6kmek.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a new client and connect to the server
client = MongoClient(uri)
db = client['user_credentials']
collection = db['users']

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        print("In token_required")
        print(request.headers)
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            
            print(token)
        if not token:
            print(token)
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            username = data.get("username")
            password = data.get("password")
            user = collection.find_one({'username': username, 'password': password})  # Fix: Use collection.find_one instead of collection.users.find_one
            print("Here", user)
            if not user:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401
            if not user["active"]:
                abort(403)
            current_user = user
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated