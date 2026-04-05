import pyrebase

# Firebase Configuration
# Replace the placeholder values with your actual Firebase project settings
# You can find these in the Firebase Console: Project Settings > General > Your apps > SDK setup and configuration
firebaseConfig = {
    "apiKey": "AIzaSyC8SdKHqQz4tGasdRylghkgi-zRaJ2GMUY",
    "authDomain": "sales-dashboard-d36b0.firebaseapp.com",
    "projectId": "sales-dashboard-d36b0",
    "storageBucket": "sales-dashboard-d36b0.firebasestorage.app",
    "messagingSenderId": "948010789748",
    "appId": "1:948010789748:web:cdd7c5c6b73a3e54861a21",
    "measurementId": "G-LG9EBMZXG5",
    "databaseURL": "https://sales-dashboard-d36b0-default-rtdb.firebaseio.com/" 
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
