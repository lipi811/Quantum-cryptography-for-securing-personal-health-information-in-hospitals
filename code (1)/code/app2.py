
from flask import Flask, render_template, redirect, url_for, flash, request,jsonify
from qiskit import QuantumCircuit, execute, Aer
from qiskit.providers.aer import AerSimulator
import mysql.connector as mq
import os
import random
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from hashlib import sha256
import quantumrandom  # Optional if you want true quantum randomness

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def dbconnection():
    con = mq.connect(host='localhost', database='quantumcrypt',user='root',password='root')
    return con

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/registerpage')
def registerpage():
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        con = dbconnection()
        cursor = con.cursor()
        cursor.execute("select * from user where email='{}' and password='{}' and role='{}'".format(email,password,role))
        res = cursor.fetchall()
        if res==[]:
            cursor.execute("insert into user (email,password,role) values ('{}','{}','{}')".format(email,password,role))
            con.commit()
            con.close()
            flash('User Registered!', 'success')
            return render_template('login.html')
        else:
            flash('Email already exist!', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        ltype = request.form.get('ltype')
        con = dbconnection()
        cursor = con.cursor()
        cursor.execute("select * from user where email='{}' and password='{}' and role='{}'".format(email,password,ltype))
        res = cursor.fetchall()
        if res!=[]:
            if ltype == 'radiologist':
                return redirect(url_for('radiologist_dashboard'))
            elif ltype == 'doctor':
                cursor.execute("select * from patient order by id desc")
                res2 = cursor.fetchall()
                return render_template('doctor_dashboard.html',res=res2)
            elif ltype == 'patient':
                return redirect(url_for('patient_dashboard'))
            else:
                flash('Invalid credentials!', 'danger')
    return render_template('login.html')


# Simulate quantum key exchange using Qiskit
def simulate_quantum_key_exchange(key_size_bytes=16):
    # Create a quantum circuit
    num_qubits = key_size_bytes * 8  # Each byte = 8 bits
    qc = QuantumCircuit(num_qubits, num_qubits)

    # Apply Hadamard gate to all qubits to create superposition
    qc.h(range(num_qubits))

    # Measure the qubits to collapse them to a definite state (0 or 1)
    qc.measure(range(num_qubits), range(num_qubits))

    # Execute the quantum circuit on a simulator
    simulator = AerSimulator()
    result = execute(qc, simulator, shots=1).result()

    # Extract the quantum random bits
    quantum_bits = result.get_counts(qc)
    binary_key = list(quantum_bits.keys())[0]

    # Convert binary key to hexadecimal (or base64) for compatibility
    hex_key = hex(int(binary_key, 2))[2:].zfill(key_size_bytes * 2)  # Ensure it's the correct length
    return hex_key

# Encrypt data with AES
def encrypt_data(data, binary_key):
    key = bytes(binary_key, 'utf-8')[:16]  # AES requires a 128-bit key (16 bytes)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    signature = sha256(padded_data).hexdigest()
    return iv + encrypted_data, signature  # Prepend IV for decryption

# Encrypt image with AES
def encrypt_image(input_path, binary_key):
    key = bytes(binary_key, 'utf-8')[:16]  # AES requires a 128-bit key (16 bytes)
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv

    with open(input_path, 'rb') as file:
        image_data = file.read()

    encrypted_data = cipher.encrypt(pad(image_data, AES.block_size))
    encrypted_image = iv + encrypted_data
    signature = sha256(encrypted_image).hexdigest()

    encrypted_image_path = os.path.join('static/uploads', f"encrypted_{os.path.basename(input_path)}")
    with open(encrypted_image_path, 'wb') as file:
        file.write(encrypted_image)

    os.remove(input_path)  # Remove the original file
    return encrypted_image_path, signature

@app.route('/radiologist_dashboard', methods=['POST', 'GET'])
def radiologist_dashboard():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        address = request.form.get('address')
        disease_type = request.form.get('disease_type')
        medical_image = request.files['medical_image']

        original_image_path = os.path.join('static/uploads', medical_image.filename)
        medical_image.save(original_image_path)

        # Simulate quantum key exchange (using Qiskit)
        quantum_key = simulate_quantum_key_exchange()
        print(f"Quantum Key (Binary): {quantum_key}")

        encrypted_name, signature_name = encrypt_data(name, quantum_key)
        encrypted_age, signature_age = encrypt_data(age, quantum_key)
        encrypted_gender, signature_gender = encrypt_data(gender, quantum_key)
        encrypted_phone, signature_phone = encrypt_data(phone, quantum_key)
        encrypted_address, signature_address = encrypt_data(address, quantum_key)
        encrypted_disease_type, signature_disease = encrypt_data(disease_type, quantum_key)
        encrypted_image_path, image_signature = encrypt_image(original_image_path, quantum_key)
        
        print("Encrypted Name Size:", len(encrypted_name))
        print("Encrypted Age Size:", len(encrypted_age))
        print("Encrypted Gender Size:", len(encrypted_gender))
        print("Encrypted Phone Size:", len(encrypted_phone))
        print("Encrypted Address Size:", len(encrypted_address))
        print("Encrypted Disease Type Size:", len(encrypted_disease_type))
        print("Encrypted Image Path Size:", len(encrypted_image_path))

        try:
            con = dbconnection()
            cursor = con.cursor()
            cursor.execute(""" 
                INSERT INTO patient (name, age, gender, phone, address, disease_type, medical_image)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (encrypted_name, encrypted_age, encrypted_gender, encrypted_phone,
                  encrypted_address, encrypted_disease_type, encrypted_image_path))

            patient_id = cursor.lastrowid
            cursor.execute(""" 
                INSERT INTO signatures (name, age, gender, phone, address, diseasetype, img, pid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (signature_name, signature_age, signature_gender, signature_phone,
                  signature_address, signature_disease, image_signature, patient_id))
            con.commit()
            flash(f"Data securely saved! Use this Quantum Key for decryption: {quantum_key}", 'success')
        except Exception as e:
            flash(f"Error saving data: {e}", 'danger')
        finally:
            cursor.close()
            con.close()

    return render_template('radiologist_dashboard.html')


from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# Decrypt data with AES
def decrypt_data(encrypted_data, hex_key):
    # Convert the hexadecimal key back to bytes
    key = bytes.fromhex(hex_key)
    
    # Extract the IV (first 16 bytes) and the encrypted content (remaining part)
    iv = encrypted_data[:16]
    encrypted_content = encrypted_data[16:]

    print("Key (Hex):", hex_key)
    print("Key (Bytes):", key)
    print("IV:", iv)
    print("Encrypted Content:", encrypted_content[:50])  # Print first 50 bytes of encrypted content for debugging

    try:
        # Create AES cipher object with CBC mode
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decrypt the data and remove padding
        decrypted_data = unpad(cipher.decrypt(encrypted_content), AES.block_size)
        
        # Return the decrypted data as a string
        return decrypted_data.decode('utf-8')
    
    except ValueError as e:
        # Handle incorrect padding
        print("Error during decryption: Padding is incorrect.")
        return None

# Decrypt image with AES
def decrypt_image(encrypted_image_path, hex_key):
    key = bytes.fromhex(hex_key)

    # Read the encrypted image from file
    with open(encrypted_image_path, 'rb') as file:
        encrypted_image = file.read()

    # Extract the IV (first 16 bytes) and the encrypted content (remaining part)
    iv = encrypted_image[:16]
    encrypted_content = encrypted_image[16:]

    print("Key (Hex):", hex_key)
    print("Key (Bytes):", key)
    print("IV:", iv)
    print("Encrypted Image Content:", encrypted_content[:50])  # Print first 50 bytes for debugging

    try:
        # Create AES cipher object with CBC mode
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decrypt the image data and remove padding
        decrypted_image_data = unpad(cipher.decrypt(encrypted_content), AES.block_size)
        
        # Return the decrypted image data in base64 encoding for rendering in HTML
        return base64.b64encode(decrypted_image_data).decode('utf-8')
    
    except ValueError as e:
        # Handle incorrect padding
        print("Error during decryption: Padding is incorrect.")
        return None


@app.route('/docdecryptdata', methods=['POST', 'GET'])
def doc_decrypt_data():
    if request.method == 'POST':
        patient_id = request.form.get('patientid')
        hex_key = request.form.get('key')

        # Ensure the provided key is of the correct length (32 hex digits for 128 bits)
        if len(hex_key) != 32:
            flash("Invalid key length. Please use a 128-bit hexadecimal key.", 'danger')
            return render_template('docdecryptdata.html')

        # Connect to the database to retrieve the patient's encrypted data
        con = dbconnection()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM patient WHERE id=%s", (patient_id,))
        patient = cursor.fetchone()

        # If no patient data is found, show an error
        if not patient:
            flash("No data found for the provided patient ID.", 'danger')
            return render_template('docres.html')

        # Extract the encrypted data fields from the database
        encrypted_name, encrypted_age, encrypted_gender, encrypted_phone, encrypted_address, encrypted_disease_type, encrypted_image_path = patient[1:]

        # Decrypt each field using the provided hex key
        decrypted_name = decrypt_data(encrypted_name, hex_key)
        decrypted_age = decrypt_data(encrypted_age, hex_key)
        decrypted_gender = decrypt_data(encrypted_gender, hex_key)
        decrypted_phone = decrypt_data(encrypted_phone, hex_key)
        decrypted_address = decrypt_data(encrypted_address, hex_key)
        decrypted_disease_type = decrypt_data(encrypted_disease_type, hex_key)
        
        # Decrypt the image path (image data)
        decrypted_image = decrypt_image(encrypted_image_path, hex_key)

        # Render the decrypted data in the result page
        return render_template(
            'docres.html',
            id=patient_id,
            name=decrypted_name,
            age=decrypted_age,
            gender=decrypted_gender,
            phone=decrypted_phone,
            address=decrypted_address,
            disease_type=decrypted_disease_type,
            image=decrypted_image
        )

    return render_template('docdecryptdata.html')
def gensignature(data):
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    signature = sha256(padded_data).hexdigest()
    return signature
    

@app.route('/gensignature' , methods=['POST', 'GET'])
def generatesignature():
    print("called")
    data = request.get_json()
    patient_id = data.get('patient_id')
    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')
    phone = data.get('phone')
    address = data.get('address')
    disease_type = data.get('disease_type')
    print(disease_type)
    
    namesig = gensignature(name)
    agesig = gensignature(age)
    gendersig = gensignature(gender)
    phonesig = gensignature(phone)
    addresssig = gensignature(address)
    disease_typesig = gensignature(disease_type)
    
    con = dbconnection()
    cursor = con.cursor()

    query = """
        SELECT * FROM signatures 
        WHERE name = %s 
        AND age = %s 
        AND gender = %s 
        AND phone = %s 
        AND address = %s 
        AND diseasetype = %s 
        AND pid = %s
    """

    # Using a tuple to safely pass the variables to the query
    cursor.execute(query, (namesig, agesig, gendersig, phonesig, addresssig, disease_typesig, int(patient_id)))

    # Fetch the result
    patient = cursor.fetchone()
    print(patient)
    if patient:
        return jsonify({"verified": True})
    else:
        return jsonify({"verified": False})
    
    
if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True)
