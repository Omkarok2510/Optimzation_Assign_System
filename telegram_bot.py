import sqlite3
import requests
import random
import math
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from datetime import datetime

# ====== CONFIGURATION ====== #
FLASK_SERVER_URL = "https://2ba8-2402-3a80-43f1-c518-b9e8-d310-5900-7300.ngrok-free.app/submit_complaint"

# Technician data - 50 technicians across Ahmednagar district with phone numbers
technicians = [
    {"id": 1, "name": "Ajay Patil", "location": "Ahmednagar City", "lat": 19.0952, "lon": 74.7496, "efficiency": 0.8, "phone": "+919876543210"},
    {"id": 2, "name": "Priya Deshmukh", "location": "Pathardi", "lat": 19.1728, "lon": 75.1783, "efficiency": 0.6, "phone": "+919876543211"},
    {"id": 3, "name": "Ravi Shinde", "location": "Shevgaon", "lat": 19.3501, "lon": 75.2334, "efficiency": 0.9, "phone": "+919876543212"},
    {"id": 4, "name": "Anjali Jadhav", "location": "Kopargaon", "lat": 19.8823, "lon": 74.4778, "efficiency": 0.7, "phone": "+919876543213"},
    {"id": 5, "name": "Vikram Gaikwad", "location": "Shrirampur", "lat": 19.6123, "lon": 74.6554, "efficiency": 0.75, "phone": "+919876543214"},
    {"id": 6, "name": "Sneha Pawar", "location": "Newasa", "lat": 19.5517, "lon": 75.0102, "efficiency": 0.85, "phone": "+919876543215"},
    {"id": 7, "name": "Rajesh More", "location": "Rahuri", "lat": 19.3907, "lon": 74.6498, "efficiency": 0.78, "phone": "+919876543216"},
    {"id": 8, "name": "Meena Chavan", "location": "Sangamner", "lat": 19.5678, "lon": 74.2119, "efficiency": 0.82, "phone": "+919876543217"},
    {"id": 9, "name": "Sanjay Kulkarni", "location": "Akole", "lat": 19.5416, "lon": 73.9987, "efficiency": 0.68, "phone": "+919876543218"},
    {"id": 10, "name": "Pooja Nimbalkar", "location": "Parner", "lat": 19.0034, "lon": 74.4432, "efficiency": 0.72, "phone": "+919876543219"},
    {"id": 11, "name": "Amit Thorat", "location": "Shrigonda", "lat": 18.6152, "lon": 74.6989, "efficiency": 0.91, "phone": "+919876543220"},
    {"id": 12, "name": "Neha Salunkhe", "location": "Karjat", "lat": 18.5507, "lon": 75.0118, "efficiency": 0.65, "phone": "+919876543221"},
    {"id": 13, "name": "Rahul Bhosale", "location": "Jamkhed", "lat": 18.7209, "lon": 75.3221, "efficiency": 0.79, "phone": "+919876543222"},
    {"id": 14, "name": "Kavita Kale", "location": "Nagar", "lat": 19.9973, "lon": 73.7898, "efficiency": 0.83, "phone": "+919876543223"},
    {"id": 15, "name": "Deepak Wagh", "location": "Pimpalgaon", "lat": 19.2345, "lon": 74.8765, "efficiency": 0.77, "phone": "+919876543224"},
    {"id": 16, "name": "Swati Ghorpade", "location": "Belapur", "lat": 19.4567, "lon": 74.9876, "efficiency": 0.88, "phone": "+919876543225"},
    {"id": 17, "name": "Vishal Nikam", "location": "Nimgaon", "lat": 19.7890, "lon": 74.6543, "efficiency": 0.74, "phone": "+919876543226"},
    {"id": 18, "name": "Anita Phadnis", "location": "Takli", "lat": 19.6789, "lon": 74.4321, "efficiency": 0.81, "phone": "+919876543227"},
    {"id": 19, "name": "Mahesh Sathe", "location": "Wadala", "lat": 19.5432, "lon": 74.3210, "efficiency": 0.69, "phone": "+919876543228"},
    {"id": 20, "name": "Sunita Ghule", "location": "Kolhar", "lat": 19.4321, "lon": 74.2109, "efficiency": 0.92, "phone": "+919876543229"},
    {"id": 21, "name": "Prakash Dhamale", "location": "Pachora", "lat": 19.3210, "lon": 74.1098, "efficiency": 0.71, "phone": "+919876543230"},
    {"id": 22, "name": "Manisha Kadu", "location": "Lasur", "lat": 19.2109, "lon": 74.0987, "efficiency": 0.84, "phone": "+919876543231"},
    {"id": 23, "name": "Dinesh Borse", "location": "Ghoti", "lat": 19.1098, "lon": 74.0876, "efficiency": 0.76, "phone": "+919876543232"},
    {"id": 24, "name": "Rekha Shilimkar", "location": "Samsherpur", "lat": 19.0987, "lon": 74.0765, "efficiency": 0.89, "phone": "+919876543233"},
    {"id": 25, "name": "Nitin Khade", "location": "Kedgaon", "lat": 19.0876, "lon": 74.0654, "efficiency": 0.73, "phone": "+919876543234"},
    {"id": 26, "name": "Shweta Bhandare", "location": "Shirdi", "lat": 19.7654, "lon": 74.4765, "efficiency": 0.8, "phone": "+919876543235"},
    {"id": 27, "name": "Suresh Khandagale", "location": "Rahata", "lat": 19.6543, "lon": 74.3654, "efficiency": 0.67, "phone": "+919876543236"},
    {"id": 28, "name": "Jyoti Wable", "location": "Kopargaon Rural", "lat": 19.5432, "lon": 74.2543, "efficiency": 0.9, "phone": "+919876543237"},
    {"id": 29, "name": "Arun Dhere", "location": "Sangamner Rural", "lat": 19.4321, "lon": 74.1432, "efficiency": 0.75, "phone": "+919876543238"},
    {"id": 30, "name": "Mamta Gunjal", "location": "Akole Rural", "lat": 19.3210, "lon": 74.0321, "efficiency": 0.82, "phone": "+919876543239"},
    {"id": 31, "name": "Vijay Chabukswar", "location": "Parner Rural", "lat": 19.2109, "lon": 73.9210, "efficiency": 0.78, "phone": "+919876543240"},
    {"id": 32, "name": "Sarika Pansare", "location": "Shrigonda Rural", "lat": 18.9876, "lon": 74.7654, "efficiency": 0.85, "phone": "+919876543241"},
    {"id": 33, "name": "Ganesh Sonawane", "location": "Karjat Rural", "lat": 18.8765, "lon": 74.6543, "efficiency": 0.79, "phone": "+919876543242"},
    {"id": 34, "name": "Lata Kulkarni", "location": "Jamkhed Rural", "lat": 18.7654, "lon": 74.5432, "efficiency": 0.86, "phone": "+919876543243"},
    {"id": 35, "name": "Ramesh Thakur", "location": "Rahuri Rural", "lat": 19.6543, "lon": 74.4321, "efficiency": 0.72, "phone": "+919876543244"},
    {"id": 36, "name": "Usha Devkar", "location": "Pathardi Rural", "lat": 19.5432, "lon": 75.3210, "efficiency": 0.91, "phone": "+919876543245"},
    {"id": 37, "name": "Harish Bansode", "location": "Shevgaon Rural", "lat": 19.4321, "lon": 75.2109, "efficiency": 0.68, "phone": "+919876543246"},
    {"id": 38, "name": "Asha Waghmare", "location": "Newasa Rural", "lat": 19.3210, "lon": 75.1098, "efficiency": 0.83, "phone": "+919876543247"},
    {"id": 39, "name": "Sunil Dhavale", "location": "Rahata Rural", "lat": 19.2109, "lon": 75.0987, "efficiency": 0.77, "phone": "+919876543248"},
    {"id": 40, "name": "Ranjana Gaware", "location": "Shirdi Rural", "lat": 19.1098, "lon": 75.0876, "efficiency": 0.89, "phone": "+919876543249"},
    {"id": 41, "name": "Anil Bhor", "location": "Nagar Rural", "lat": 19.0987, "lon": 75.0765, "efficiency": 0.74, "phone": "+919876543250"},
    {"id": 42, "name": "Kiran Kate", "location": "Pimpalgaon Rural", "lat": 19.0876, "lon": 75.0654, "efficiency": 0.81, "phone": "+919876543251"},
    {"id": 43, "name": "Mohan Dhotre", "location": "Belapur Rural", "lat": 19.0765, "lon": 75.0543, "efficiency": 0.92, "phone": "+919876543252"},
    {"id": 44, "name": "Geeta Gaidhani", "location": "Nimgaon Rural", "lat": 19.0654, "lon": 75.0432, "efficiency": 0.7, "phone": "+919876543253"},
    {"id": 45, "name": "Rajiv Kharat", "location": "Takli Rural", "lat": 19.0543, "lon": 75.0321, "efficiency": 0.84, "phone": "+919876543254"},
    {"id": 46, "name": "Smita Kshirsagar", "location": "Wadala Rural", "lat": 19.0432, "lon": 75.0210, "efficiency": 0.76, "phone": "+919876543255"},
    {"id": 47, "name": "Vivek Bhalerao", "location": "Kolhar Rural", "lat": 19.0321, "lon": 75.0109, "efficiency": 0.9, "phone": "+919876543256"},
    {"id": 48, "name": "Preeti Deshpande", "location": "Pachora Rural", "lat": 19.0210, "lon": 75.0098, "efficiency": 0.73, "phone": "+919876543257"},
    {"id": 49, "name": "Nilesh Jadhav", "location": "Lasur Rural", "lat": 19.0109, "lon": 75.0087, "efficiency": 0.87, "phone": "+919876543258"},
    {"id": 50, "name": "Divya Mule", "location": "Ghoti Rural", "lat": 19.0098, "lon": 75.0076, "efficiency": 0.8, "phone": "+919876543259"}
]

# Location coordinates covering Ahmednagar district
location_map = {
    "Ahmednagar City": (19.0952, 74.7496),
    "Pathardi": (19.1728, 75.1783),
    "Shevgaon": (19.3501, 75.2334),
    "Kopargaon": (19.8823, 74.4778),
    "Shrirampur": (19.6123, 74.6554),
    "Newasa": (19.5517, 75.0102),
    "Rahuri": (19.3907, 74.6498),
    "Sangamner": (19.5678, 74.2119),
    "Akole": (19.5416, 73.9987),
    "Parner": (19.0034, 74.4432),
    "Shrigonda": (18.6152, 74.6989),
    "Karjat": (18.5507, 75.0118),
    "Jamkhed": (18.7209, 75.3221),
    "Nagar": (19.9973, 73.7898),
    "Pimpalgaon": (19.2345, 74.8765),
    "Belapur": (19.4567, 74.9876),
    "Nimgaon": (19.7890, 74.6543),
    "Takli": (19.6789, 74.4321),
    "Wadala": (19.5432, 74.3210),
    "Kolhar": (19.4321, 74.2109),
    "Pachora": (19.3210, 74.1098),
    "Lasur": (19.2109, 74.0987),
    "Ghoti": (19.1098, 74.0876),
    "Samsherpur": (19.0987, 74.0765),
    "Kedgaon": (19.0876, 74.0654),
    "Shirdi": (19.7654, 74.4765),
    "Rahata": (19.6543, 74.3654),
    "Kopargaon Rural": (19.5432, 74.2543),
    "Sangamner Rural": (19.4321, 74.1432),
    "Akole Rural": (19.3210, 74.0321),
    "Parner Rural": (19.2109, 73.9210),
    "Shrigonda Rural": (18.9876, 74.7654),
    "Karjat Rural": (18.8765, 74.6543),
    "Jamkhed Rural": (18.7654, 74.5432),
    "Rahuri Rural": (19.6543, 74.4321),
    "Pathardi Rural": (19.5432, 75.3210),
    "Shevgaon Rural": (19.4321, 75.2109),
    "Newasa Rural": (19.3210, 75.1098),
    "Rahata Rural": (19.2109, 75.0987),
    "Shirdi Rural": (19.1098, 75.0876),
    "Nagar Rural": (19.0987, 75.0765),
    "Pimpalgaon Rural": (19.0876, 75.0654),
    "Belapur Rural": (19.0765, 75.0543),
    "Nimgaon Rural": (19.0654, 75.0432),
    "Takli Rural": (19.0543, 75.0321),
    "Wadala Rural": (19.0432, 75.0210),
    "Kolhar Rural": (19.0321, 75.0109),
    "Pachora Rural": (19.0210, 75.0098),
    "Lasur Rural": (19.0109, 75.0087),
    "Ghoti Rural": (19.0098, 75.0076)
}

# [Rest of the code remains the same...]
# ========================== #

# Helper functions
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates (Haversine formula)"""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * 
         math.cos(math.radians(lat2)) * math.sin(dlon/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def init_db():
    """Initialize local SQLite database"""
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            problem TEXT,
            address TEXT,
            contact_no TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def store_complaint(chat_id, problem, address, contact_no):
    """Store complaint in local database"""
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints (chat_id, problem, address, contact_no)
        VALUES (?, ?, ?, ?)
    """, (chat_id, problem, address, contact_no))
    conn.commit()
    conn.close()

def assign_technician(problem_type, user_address):
    """Smart technician assignment with Monte Carlo simulation"""
    user_location = next((loc for name, loc in location_map.items() 
                         if name.lower() in user_address.lower()), 
                        (19.1, 74.7))  # Default to Ahmednagar

    scores = {
        tech["id"]: sum(1 for _ in range(1000) if random.random() < tech["efficiency"])/1000 
                   / (calculate_distance(user_location[0], user_location[1], 
                                        tech["lat"], tech["lon"]) + 1)
        for tech in technicians
    }
    return next(t for t in technicians if t["id"] == max(scores, key=scores.get))

# Conversation handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome! Please describe your problem:")
    return PROBLEM

async def problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["problem"] = update.message.text
    await update.message.reply_text("Please provide your address (include town name):")
    return ADDRESS

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["address"] = update.message.text
    await update.message.reply_text("Please share your contact number:")
    return CONTACT

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.chat_id
    contact_no = update.message.text
    problem = context.user_data["problem"]
    address = context.user_data["address"]

    # Local storage
    store_complaint(chat_id, problem, address, contact_no)
    assigned_tech = assign_technician(problem, address)
    
    # Server communication
    try:
        response = requests.post(
            FLASK_SERVER_URL,
            json={
                "chat_id": chat_id,
                "problem": problem,
                "address": address,
                "contact_no": contact_no
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            response_data = response.json()
            message = (f"✅ Complaint #{response_data.get('complaint_id', 'N/A')} registered!\n"
          f"🔧 Technician: {assigned_tech['name']}\n"
          f"📞 Contact: {assigned_tech['phone']}\n"
          f"🔗 Blockchain: {response_data.get('blockchain_hash', 'N/A')}")
        else:
            error = response.json().get('error', 'Unknown error') if response.content else 'Empty response'
            message = (f"⚠️ Saved locally (server error {response.status_code})\n"
                      f"🔧 Technician: {assigned_tech['name']}\n"
                      f"📞 Contact: {assigned_tech['phone']}\n"
                      f"❌ Error: {error}")
    except Exception as e:
        message = (f"⚠️ Saved locally (network error)\n"
                  f"🔧 Technician: {assigned_tech['name']}\n"
                  f"📞 Contact: {assigned_tech['phone']}\n"
                  f"❌ Error: {str(e)}")

    await update.message.reply_text(message)
    
    # Digital twin logging
    with open("digital_twin_log.txt", "a") as f:
        f.write(f"[{datetime.now()}] {chat_id}|{problem}|{address}|{assigned_tech['name']}\n")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Complaint cancelled.")
    return ConversationHandler.END

# Conversation states
PROBLEM, ADDRESS, CONTACT = range(3)

def main():
    init_db()
    application = Application.builder().token("7922002419:AAGsGo2deXJC4P2IPAoOg7F_fT2GmjE2K_Q").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, problem)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
