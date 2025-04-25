from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from datetime import datetime
import random
import math

app = Flask(__name__)
CORS(app)

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('complaints.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ensure 'timestamp' column exists in complaints table
def ensure_timestamp_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT timestamp FROM complaints LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE complaints ADD COLUMN timestamp DATETIME")
        cursor.execute("UPDATE complaints SET timestamp = datetime('now') WHERE timestamp IS NULL")
        conn.commit()
    conn.close()

def ensure_technician_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT technician_id FROM complaints LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE complaints ADD COLUMN technician_id INTEGER")
        conn.commit()
    conn.close()

# Initialize database tables
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create complaints table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            problem TEXT,
            address TEXT,
            contact_no TEXT,
            timestamp DATETIME,
            technician_id INTEGER
        )
    """)

    # Create technicians table with additional fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact_no TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT,
            efficiency REAL,
            location TEXT
        )
    """)

    # Insert 50 technicians if empty
    cursor.execute("SELECT COUNT(*) FROM technicians")
    if cursor.fetchone()[0] == 0:
        technicians_data = [
            # Ahmednagar City and nearby
            ('Ajay Patil', '+919876543210', 19.0952, 74.7496, 'available', 0.85, 'Ahmednagar City'),
            ('Priya Deshmukh', '+919876543211', 19.1050, 74.7590, 'available', 0.78, 'Ahmednagar City'),
            ('Rahul Sharma', '+919876543212', 19.0850, 74.7390, 'available', 0.82, 'Ahmednagar City'),
            
            # Pathardi region
            ('Vikram Jadhav', '+919876543213', 19.1728, 75.1783, 'available', 0.75, 'Pathardi'),
            ('Neha Gaikwad', '+919876543214', 19.1820, 75.1880, 'available', 0.88, 'Pathardi'),
            
            # Shevgaon region
            ('Sanjay Kulkarni', '+919876543215', 19.3501, 75.2334, 'available', 0.79, 'Shevgaon'),
            ('Anjali Pawar', '+919876543216', 19.3600, 75.2430, 'available', 0.91, 'Shevgaon'),
            
            # Kopargaon region
            ('Rajesh More', '+919876543217', 19.8823, 74.4778, 'available', 0.83, 'Kopargaon'),
            ('Meena Chavan', '+919876543218', 19.8920, 74.4870, 'available', 0.76, 'Kopargaon'),
            
            # Shrirampur region
            ('Amit Thorat', '+919876543219', 19.6123, 74.6554, 'available', 0.89, 'Shrirampur'),
            ('Sneha Salunkhe', '+919876543220', 19.6220, 74.6650, 'available', 0.72, 'Shrirampur'),
            
            # Newasa region
            ('Ravi Shinde', '+919876543221', 19.5517, 75.0102, 'available', 0.81, 'Newasa'),
            ('Kavita Kale', '+919876543222', 19.5610, 75.0200, 'available', 0.94, 'Newasa'),
            
            # Rahuri region
            ('Deepak Wagh', '+919876543223', 19.3907, 74.6498, 'available', 0.77, 'Rahuri'),
            ('Swati Ghorpade', '+919876543224', 19.4000, 74.6590, 'available', 0.85, 'Rahuri'),
            
            # Sangamner region
            ('Vishal Nikam', '+919876543225', 19.5678, 74.2119, 'available', 0.79, 'Sangamner'),
            ('Anita Phadnis', '+919876543226', 19.5770, 74.2210, 'available', 0.92, 'Sangamner'),
            
            # Akole region
            ('Mahesh Sathe', '+919876543227', 19.5416, 73.9987, 'available', 0.81, 'Akole'),
            ('Sunita Ghule', '+919876543228', 19.5510, 74.0080, 'available', 0.73, 'Akole'),
            
            # Parner region
            ('Prakash Dhamale', '+919876543229', 19.0034, 74.4432, 'available', 0.88, 'Parner'),
            ('Manisha Kadu', '+919876543230', 19.0130, 74.4530, 'available', 0.75, 'Parner'),
            
            # Shrigonda region
            ('Dinesh Borse', '+919876543231', 18.6152, 74.6989, 'available', 0.82, 'Shrigonda'),
            ('Rekha Shilimkar', '+919876543232', 18.6250, 74.7080, 'available', 0.91, 'Shrigonda'),
            
            # Karjat region
            ('Nitin Khade', '+919876543233', 18.5507, 75.0118, 'available', 0.76, 'Karjat'),
            ('Shweta Bhandare', '+919876543234', 18.5600, 75.0210, 'available', 0.84, 'Karjat'),
            
            # Jamkhed region
            ('Suresh Khandagale', '+919876543235', 18.7209, 75.3221, 'available', 0.89, 'Jamkhed'),
            ('Jyoti Wable', '+919876543236', 18.7300, 75.3320, 'available', 0.78, 'Jamkhed'),
            
            # Nagar region
            ('Arun Dhere', '+919876543237', 19.9973, 73.7898, 'available', 0.83, 'Nagar'),
            ('Mamta Gunjal', '+919876543238', 19.9870, 73.7990, 'available', 0.92, 'Nagar'),
            
            # Pimpalgaon region
            ('Vijay Chabukswar', '+919876543239', 19.2345, 74.8765, 'available', 0.77, 'Pimpalgaon'),
            ('Sarika Pansare', '+919876543240', 19.2440, 74.8860, 'available', 0.85, 'Pimpalgaon'),
            
            # Belapur region
            ('Ganesh Sonawane', '+919876543241', 19.4567, 74.9876, 'available', 0.81, 'Belapur'),
            ('Lata Kulkarni', '+919876543242', 19.4660, 74.9970, 'available', 0.93, 'Belapur'),
            
            # Nimgaon region
            ('Ramesh Thakur', '+919876543243', 19.7890, 74.6543, 'available', 0.79, 'Nimgaon'),
            ('Usha Devkar', '+919876543244', 19.7990, 74.6640, 'available', 0.86, 'Nimgaon'),
            
            # Takli region
            ('Harish Bansode', '+919876543245', 19.6789, 74.4321, 'available', 0.82, 'Takli'),
            ('Asha Waghmare', '+919876543246', 19.6880, 74.4420, 'available', 0.75, 'Takli'),
            
            # Wadala region
            ('Sunil Dhavale', '+919876543247', 19.5432, 74.3210, 'available', 0.91, 'Wadala'),
            ('Ranjana Gaware', '+919876543248', 19.5530, 74.3310, 'available', 0.78, 'Wadala'),
            
            # Kolhar region
            ('Anil Bhor', '+919876543249', 19.4321, 74.2109, 'available', 0.84, 'Kolhar'),
            ('Kiran Kate', '+919876543250', 19.4420, 74.2200, 'available', 0.77, 'Kolhar'),
            
            # Pachora region
            ('Mohan Dhotre', '+919876543251', 19.3210, 74.1098, 'available', 0.89, 'Pachora'),
            ('Geeta Gaidhani', '+919876543252', 19.3310, 74.1190, 'available', 0.82, 'Pachora'),
            
            # Lasur region
            ('Rajiv Kharat', '+919876543253', 19.2109, 74.0987, 'available', 0.76, 'Lasur'),
            ('Smita Kshirsagar', '+919876543254', 19.2200, 74.1080, 'available', 0.93, 'Lasur'),
            
            # Ghoti region
            ('Vivek Bhalerao', '+919876543255', 19.1098, 74.0876, 'available', 0.81, 'Ghoti'),
            ('Preeti Deshpande', '+919876543256', 19.1190, 74.0970, 'available', 0.88, 'Ghoti'),
            
            # Samsherpur region
            ('Nilesh Jadhav', '+919876543257', 19.0987, 74.0765, 'available', 0.79, 'Samsherpur'),
            ('Divya Mule', '+919876543258', 19.1080, 74.0860, 'available', 0.92, 'Samsherpur'),
            
            # Kedgaon region
            ('Sachin Nimbalkar', '+919876543259', 19.0876, 74.0654, 'available', 0.85, 'Kedgaon')
        ]
        
        cursor.executemany("""
            INSERT INTO technicians (name, contact_no, latitude, longitude, status, efficiency, location) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, technicians_data)

    conn.commit()
    conn.close()

# Call init functions
init_db()
ensure_timestamp_column()
ensure_technician_column()

# Dashboard route - loads data to template
@app.route('/')
def dashboard():
    conn = get_db_connection()
    complaints = conn.execute('SELECT * FROM complaints ORDER BY timestamp DESC').fetchall()
    technicians = conn.execute('SELECT * FROM technicians').fetchall()
    conn.close()

    complaints_list = [list(row) for row in complaints]
    technicians_list = [list(row) for row in technicians]

    return render_template('dashboard.html',
                           complaints=complaints_list,
                           technicians=technicians_list)

# API to fetch complaints + technicians (AJAX use)
@app.route('/api/data')
def get_data():
    conn = get_db_connection()
    complaints = conn.execute('SELECT * FROM complaints ORDER BY timestamp DESC').fetchall()
    technicians = conn.execute('SELECT * FROM technicians').fetchall()
    conn.close()

    return jsonify({
        'complaints': [dict(row) for row in complaints],
        'technicians': [dict(row) for row in technicians]
    })

# Complaint submission endpoint
@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    try:
        data = request.get_json()

        required_fields = ['chat_id', 'problem', 'address', 'contact_no']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user location from address
        user_location = None
        for loc_name, (lat, lon) in location_map.items():
            if loc_name.lower() in data['address'].lower():
                user_location = (lat, lon)
                break
        
        if not user_location:
            user_location = (19.0952, 74.7496)  # Default to Ahmednagar City

        # Find best available technician using distance and efficiency
        available_techs = cursor.execute("""
            SELECT * FROM technicians WHERE status = 'available'
        """).fetchall()

        if not available_techs:
            conn.close()
            return jsonify({"message": "All technicians are currently busy. Please try again later."}), 503

        # Calculate scores for each technician
        best_tech = None
        best_score = -1
        
        for tech in available_techs:
            distance = calculate_distance(user_location[0], user_location[1], 
                                       tech['latitude'], tech['longitude'])
            # Score combines efficiency and proximity (higher is better)
            score = tech['efficiency'] / (distance + 1)  # +1 to avoid division by zero
            
            if score > best_score:
                best_score = score
                best_tech = tech

        # Insert complaint with technician assigned
        cursor.execute("""
            INSERT INTO complaints (chat_id, problem, address, contact_no, technician_id, timestamp)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (data['chat_id'], data['problem'], data['address'], data['contact_no'], best_tech['id']))

        # Update technician status to busy
        cursor.execute("""
            UPDATE technicians SET status = 'busy' WHERE id = ?
        """, (best_tech['id'],))

        conn.commit()
        complaint_id = cursor.lastrowid
        conn.close()

        return jsonify({
            "message": f"Complaint registered and assigned to technician {best_tech['name']}",
            "complaint_id": complaint_id,
            "technician": dict(best_tech),
            "technician_contact": best_tech['contact_no']
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper function to calculate distance between coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates (Haversine formula)"""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**26
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Location coordinates map
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
    "Kedgaon": (19.0876, 74.0654)
}

# Run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)