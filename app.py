import logging
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO
import mysql.connector
import re
import requests
from flask_cors import CORS
from datetime import datetime
from collections import Counter

app = Flask(__name__)
app.secret_key = "dikahdmi"
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app, origins=["http://192.168.1.8"])

logging.basicConfig(level=logging.DEBUG)
ESP32_IP = "http://192.168.1.104"

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="robotgd2",
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def execute_query(query, params):
    conn = get_db_connection()
    if not conn:
        return None, "Maaf, terjadi kesalahan pada koneksi database. Coba lagi nanti."
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result, None
    except mysql.connector.Error as err:
        print(f"Query error: {err}")
        return None, "Maaf, terjadi kesalahan pada query database. Coba lagi nanti."
    finally:
        cursor.close()
        conn.close()

def execute_query_non_fetch(query, params):
    conn = get_db_connection()
    if not conn:
        return None, "Maaf, terjadi kesalahan pada koneksi database."
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        conn.commit()
        return None, None
    except mysql.connector.Error as err:
        print(f"Query error: {err}")
        return None, "Maaf, terjadi kesalahan pada query database."
    finally:
        cursor.close()
        conn.close()

def find_room(search_term):
    synonyms = {
        "laboratorium komputer": ["lab komputer", "laboratorium komputer"],
        "ruang tu": ["ruang tata usaha", "ruang tu"],
        "ruang kaprodi": ["ruang kepala program studi", "ruang kaprodi"],
        "ruang sidang": ["ruang rapat", "ruang sidang"],
        "laboratorium utama": ["lab utama", "laboratorium utama"],
        "ruang staff": ["ruang staf", "ruang staff"],
        "ruang alat-alat laboratorium": ["ruang alat", "ruang alat-alat laboratorium"],
        "ruang ict": ["ruang kerja ict", "ruang ict", "ict"],
        "ruang bengkel": ["ruang bengkel peralatan", "bengkel", "ruang bengkel"],
        "laboratorium elektronika": ["lab elektronika", "laboratorium elektronika"],
        "laboratorium mekatronika": ["lab mekatronika", "laboratorium mekatronika"],
        "laboratorium riset": ["lab riset", "laboratorium riset"],
        "ruang dosen": ["dosen", "ruang dosen"]
    }
    for key, values in synonyms.items():
        if search_term.lower() in [v.lower() for v in values]:
            search_term = key
            break

    query = """
        SELECT r.id, r.nomor, r.nama, l.nomor AS lantai, l.deskripsi 
        FROM ruangan r
        JOIN lantai l ON r.lantai_id = l.id
        WHERE LOWER(r.nama) LIKE %s OR r.nomor LIKE %s
    """
    result, error = execute_query(query, (f"%{search_term}%", f"%{search_term}%"))
    if error:
        return None, error
    return result[0] if result else None, None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin")
def admin():
    if "admin_logged_in" not in session:
        return redirect(url_for("login"))
    return render_template("admin.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = get_db_connection()
        if not conn:
            return "Database connection error"
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM admin WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            return "Login gagal, periksa kembali username dan password Anda."
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower().strip()
    user_message = re.sub(r'[^\w\s]', '', user_message)
    
    if not user_message:
        return jsonify({"response": "Halo!, Ada yang bisa saya bantu? Silakan tanyakan lokasi ruangan atau fasilitas di gedung ini"})
    
    response = ""
    
    def get_rooms_in_floor(lantai_nomor):
        query = "SELECT id, deskripsi FROM lantai WHERE nomor = %s"
        lantai_data, error = execute_query(query, (lantai_nomor,))
        if error or not lantai_data:
            return None, None, error
        
        lantai_id = lantai_data[0]["id"]
        query = "SELECT nomor, nama FROM ruangan WHERE lantai_id = %s"
        ruangan, error = execute_query(query, (lantai_id,))
        return lantai_data[0], ruangan, error

    if "dimana" in user_message:
        search_term = user_message.replace("dimana", "").strip()
        room, error = find_room(search_term)
        if error:
            response = error
        elif room:
            response = f"{room['nama']} ada di lantai {room['lantai']}, ruang {room['nomor']}. Silakan menuju ke sana!"
        else:
            response = f"Wah, aku tidak menemukan ruangan '{search_term}'. Bisa dicek lagi namanya?"

    elif "lantai" in user_message:
        match = re.search(r'lantai\s*(\d+)', user_message)
        if match:
            lantai_nomor = match.group(1)
            lantai_data, ruangan, error = get_rooms_in_floor(lantai_nomor)
            if error:
                response = error
            elif lantai_data:
                ruangan_list = "\n".join([f"- {r['nomor']}: {r['nama']}" for r in ruangan]) if ruangan else "Tidak ada ruangan yang terdaftar di lantai ini."
                response = f"Lantai {lantai_nomor}:{lantai_data['deskripsi']}\n{ruangan_list}"
            else:
                response = f"Maaf, aku tidak menemukan informasi untuk lantai {lantai_nomor}. Bisa coba lantai lain?"
        else:
            response = "Silakan sebutkan lantai yang ingin kamu ketahui, misalnya: ceritakan tentang lantai 3"

    elif "ruang" in user_message or "ruangan" in user_message:
        match = re.search(r'ruang(?:an)?\s*([A-Za-z0-9\s]+)', user_message)
        if match:
            nomor_ruang = match.group(1).strip()
            room, error = find_room(nomor_ruang)
            if error:
                response = error
            elif room:
                response = f"Ruang {nomor_ruang} adalah {room['nama']}, ada di lantai {room['lantai']}"
            else:
                response = f"Ups, aku tidak menemukan ruangan {nomor_ruang}. Mungkin ada kesalahan nomor?"
        else:
            response = "Silakan sebutkan nomor ruangan yang ingin dicari, misalnya: Ruang 2101 itu apa?"

    elif "fasilitas" in user_message or "ada apa" in user_message:
        query = "SELECT nomor, deskripsi FROM lantai"
        lantai_data, error = execute_query(query, ())
        if error:
            response = error
        else:
            response = "Di gedung ini, kamu bisa menemukan:\n"
            for lantai in lantai_data:
                response += f"Lantai {lantai['nomor']}: {lantai['deskripsi']}\n"
            response += "Semoga informasinya membantu ya!"
    else:
        response = (
            "Aku bisa bantu cari ruangan atau informasi gedung! Coba tanyakan:\n"
            "- Dimana Laboratorium Komputer?\n"
            "- Ceritakan tentang lantai 2\n"
            "- Ruang 2101 itu apa?\n"
            "- Fasilitas apa saja di gedung ini?"
        )
    
    return jsonify({"response": response})

@app.route('/activate_button', methods=['POST'])
def activate_button():
    try:
        data = request.get_json()
        print(f"Data diterima dari ESP32: {data}")
        logging.debug(f"Data diterima dari ESP32: {data}")

        status = data.get('status')
        
        if not status:
            raise ValueError("Status tidak ditemukan dalam request")

        if status == "active":
            print("Tombol diaktifkan oleh ESP32!")
            logging.debug("Tombol diaktifkan oleh ESP32!")
            socketio.emit('mic_button_triggered')
            return jsonify({"message": "Tombol diaktifkan!"}), 200  
        else:
            print(f"Status tidak valid: {status}")
            logging.warning(f"Status tidak valid: {status}")
            return jsonify({"message": "Status tidak valid!"}), 400

    except Exception as e:
        print(f"Error terjadi: {str(e)}")
        logging.error(f"Error terjadi: {str(e)}")
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route('/chat_with_stats', methods=['POST'])
def chat_with_stats():
    user_message = request.json.get("message", "").lower().strip()
    user_message = re.sub(r'[^\w\s]', '', user_message)
    
    # Catat pertanyaan relevan ke robot_usage
    ruangan_id = None
    is_relevant = any(keyword in user_message for keyword in ["dimana", "ruang", "ruangan", "lantai"])
    if is_relevant:
        search_term = user_message
        if "dimana" in user_message:
            search_term = user_message.replace("dimana", "").strip()
        elif "ruang" in user_message or "ruangan" in user_message:
            match = re.search(r'ruang(?:an)?\s*([A-Za-z0-9\s]+)', user_message)
            if match:
                search_term = match.group(1).strip()
        
        room, error = find_room(search_term)
        if room:
            ruangan_id = room["id"]
        
        query = "INSERT INTO robot_usage (event_type, ruangan_id, timestamp, details) VALUES (%s, %s, %s, %s)"
        execute_query_non_fetch(query, ("question", ruangan_id, datetime.now(), user_message))
        
        socketio.emit('robot_notification', {
            'message': f"Pertanyaan baru: {user_message}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'ruangan_id': ruangan_id,
            'ruangan_nama': room['nama'] if room else None
        })
    
    # Panggil fungsi chat untuk mendapatkan jawaban utama
    chat_response = chat().get_json()
    response = chat_response["response"]
    
    # Ambil pertanyaan rekomendasi dari frequent_questions_report
    query = """
        SELECT ru.details
        FROM robot_usage ru
        WHERE ru.event_type = 'question' AND ru.details IS NOT NULL
    """
    result, error = execute_query(query, ())
    if error:
        recommendation = "Apa lagi yang ingin kamu ketahui tentang gedung ini?"
    else:
        questions = [re.sub(r'[^\w\s]', '', row["details"]).lower().strip() for row in result]
        question_freq = Counter(questions)
        top_question = question_freq.most_common(1)
        recommendation = f"Orang lain sering bertanya: '{top_question[0][0]}'. Apakah kamu ingin tahu tentang itu?" if top_question else "Apa lagi yang ingin kamu ketahui tentang gedung ini?"
    
    return jsonify({
        "response": response,
        "recommendation": recommendation
    })

@app.route('/activate_button_with_stats', methods=['POST'])
def activate_button_with_stats():
    try:
        data = request.get_json()
        print(f"Data diterima dari ESP32: {data}")
        logging.debug(f"Data diterima dari ESP32: {data}")

        status = data.get('status')
        
        if not status:
            raise ValueError("Status tidak ditemukan dalam request")

        if status == "active":
            print("Tombol diaktifkan oleh ESP32!")
            logging.debug("Tombol diaktifkan oleh ESP32!")
            
            query = "INSERT INTO robot_usage (event_type, timestamp, details) VALUES (%s, %s, %s)"
            execute_query_non_fetch(query, ("activation", datetime.now(), "Lengan robot diaktifkan"))
            
            socketio.emit('robot_notification', {
                'message': "Lengan robot diaktifkan!",
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            socketio.emit('mic_button_triggered')
            return jsonify({"message": "Tombol diaktifkan!"}), 200  
        else:
            print(f"Status tidak valid: {status}")
            logging.warning(f"Status tidak valid: {status}")
            return jsonify({"message": "Status tidak valid!"}), 400

    except Exception as e:
        print(f"Error terjadi: {str(e)}")
        logging.error(f"Error terjadi: {str(e)}")
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route('/stats', methods=['GET'])
def stats():
    if "admin_logged_in" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    query = "SELECT COUNT(*) AS total FROM robot_usage WHERE event_type = 'activation'"
    result, error = execute_query(query, ())
    total_activations = result[0]["total"] if result else 0
    
    query = "SELECT COUNT(*) AS total FROM robot_usage WHERE event_type = 'question'"
    result, error = execute_query(query, ())
    total_questions = result[0]["total"] if result else 0
    
    query = """
        SELECT r.nama, r.nomor, COUNT(*) AS count
        FROM robot_usage ru 
        JOIN ruangan r ON ru.ruangan_id = r.id 
        WHERE ru.event_type = 'question' 
        GROUP BY ru.ruangan_id 
        ORDER BY count DESC 
        LIMIT 5
    """
    top_rooms, error = execute_query(query, ())
    
    return jsonify({
        "total_activations": total_activations,
        "total_questions": total_questions,
        "top_rooms": top_rooms or []
    })

@app.route('/top_room', methods=['GET'])
def top_room():
    query = """
        SELECT r.nama, r.nomor, COUNT(*) AS count
        FROM robot_usage ru 
        JOIN ruangan r ON ru.ruangan_id = r.id 
        WHERE ru.event_type = 'question' 
        GROUP BY ru.ruangan_id 
        ORDER BY count DESC 
        LIMIT 1
    """
    result, error = execute_query(query, ())
    if error or not result:
        return jsonify({"nama": None, "nomor": None, "count": 0})
    return jsonify(result[0])

@app.route('/robot_usage_details', methods=['GET'])
def robot_usage_details():
    if "admin_logged_in" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    query = """
        SELECT ru.details, ru.ruangan_id, r.nama AS ruangan_nama, ru.timestamp
        FROM robot_usage ru
        LEFT JOIN ruangan r ON ru.ruangan_id = r.id
        WHERE ru.event_type = 'question' AND ru.details IS NOT NULL
        ORDER BY ru.timestamp DESC
    """
    result, error = execute_query(query, ())
    if error:
        return jsonify({"error": error}), 500
    return jsonify(result or [])

@app.route('/frequent_questions_report', methods=['GET'])
def frequent_questions_report():
    if "admin_logged_in" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    query = """
        SELECT ru.details
        FROM robot_usage ru
        WHERE ru.event_type = 'question' AND ru.details IS NOT NULL
    """
    result, error = execute_query(query, ())
    if error:
        return jsonify({"error": error}), 500
    
    questions = [re.sub(r'[^\w\s]', '', row["details"]).lower().strip() for row in result]
    question_freq = Counter(questions)
    top_questions = [
        {"question": question, "count": count}
        for question, count in question_freq.most_common(5)
    ]
    
    top_room_data, error = execute_query(
        """
        SELECT r.nama, r.nomor, COUNT(*) AS count
        FROM robot_usage ru 
        JOIN ruangan r ON ru.ruangan_id = r.id 
        WHERE ru.event_type = 'question' 
        GROUP BY ru.ruangan_id 
        ORDER BY count DESC 
        LIMIT 1
        """,
        ()
    )
    top_room_info = top_room_data[0] if top_room_data else {"nama": None, "nomor": None, "count": 0}
    
    chart = {
        "type": "bar",
        "data": {
            "labels": [q["question"] for q in top_questions],
            "datasets": [{
                "label": "Jumlah Pertanyaan",
                "data": [q["count"] for q in top_questions],
                "backgroundColor": ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0", "#9966FF"],
                "borderColor": ["#2A8BBF", "#CC5066", "#CCA43D", "#3A9A9A", "#7A52CC"],
                "borderWidth": 1
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {"display": True, "text": "5 Pertanyaan Paling Sering Diajukan"}
            },
            "scales": {
                "x": {"title": {"display": True, "text": "Pertanyaan"}},
                "y": {"title": {"display": True, "text": "Jumlah"}, "beginAtZero": True}
            }
        }
    }
    
    return jsonify({
        "top_questions": top_questions,
        "top_room": top_room_info,
        "chart": chart
    })

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)