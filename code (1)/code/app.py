from flask import Flask, render_template, redirect, url_for, flash, request,jsonify,session
import mysql.connector as mq
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os
import base64
import quantumrandom
import random
from werkzeug.utils import secure_filename
from hashlib import sha256
from io import BytesIO
from PIL import Image
import mailing

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def dbconnection():
    con = mq.connect(host='localhost', database='quantumcrypt',user='root',password='root')
    return con



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/loginpage')
def loginpage():
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

@app.route('/docdash')
def docdash():
    did = session["did"]
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from patient where did='{}' order by id desc".format(int(did)))
    res2 = cursor.fetchall()
    return render_template('doctor_dashboard.html',res=res2)

@app.route('/patient_dashboard')
def patient_dashboard():
    pid = session["pid"]
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from patient where id='{}' order by id desc".format(int(pid)))
    res2 = cursor.fetchall()
    return render_template('patient_dashboard.html',res=res2)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        ltype = request.form.get('ltype')
        con = dbconnection()
        cursor = con.cursor()
        if ltype == 'radiologist':
            cursor.execute("select * from user where email='{}' and password='{}' and role='{}'".format(email,password,ltype))
            res = cursor.fetchall()
            if res!=[]:
                return redirect(url_for('radiologist_dashboard'))
            else:
                flash('Invalid credentials!', 'danger')
                return render_template('login.html')
        elif ltype == 'doctor':
            cursor.execute("select * from user where email='{}' and password='{}' and role='{}'".format(email,password,ltype))
            res = cursor.fetchall()
            if res!=[]:
                session['did']=res[0][0]
                return redirect(url_for('docdash'))
            else:
                flash('Invalid credentials!', 'danger')
                return render_template('login.html')
            
            
        elif ltype == 'patient':
            con2 = dbconnection()
            cursor2 = con2.cursor()
            cursor2.execute("select * from patientlogin where email='{}' and password='{}'".format(email.strip(),password.strip()))
            res2 = cursor2.fetchall()
            print(res2)
            if res2!=[]:

                print(res2)
                print("pid",res2[0][3])
                session['pid']=res2[0][3]
                return redirect(url_for('patient_dashboard'))
            else:
                flash('Invalid credentials!', 'danger')
                return render_template('login.html')
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('login.html')


# Simulate quantum key exchange
def simulate_quantum_key_exchange(key_length):
    try:
        import quantumrandom
        binary_key = ''.join(str(quantumrandom.randint(0, 1)) for _ in range(key_length))
    except Exception:
        binary_key = ''.join(str(random.randint(0, 1)) for _ in range(key_length))
    # Convert binary key to hexadecimal
    hex_key = hex(int(binary_key, 2))[2:].zfill(key_length // 4)
    return hex_key


# Encrypt data with AES
def encrypt_data(data, hex_key):
    key = bytes.fromhex(hex_key)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    signature = sha256(padded_data).hexdigest()
    return iv + encrypted_data, signature  # Prepend IV for decryption


# Encrypt image with AES
def encrypt_image(input_path, hex_key):
    key = bytes.fromhex(hex_key)
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
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from user where role='{}'".format("doctor"))
    res = cursor.fetchall()
    if res==[]:
        flash(f"Error saving data: {e}", 'danger')
        return render_template('radiologist_dashboard.html')
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        address = request.form.get('address')
        disease_type = request.form.get('disease_type')
        medical_image = request.files['medical_image']
        did = request.form.get('doctor')
        email = request.form.get('pemail')

        original_image_path = os.path.join('static/uploads', medical_image.filename)
        medical_image.save(original_image_path)

        quantum_key = simulate_quantum_key_exchange(key_length=128)
        print(f"Quantum Key (Hex): {quantum_key}")

        encrypted_name, signature_name = encrypt_data(name, quantum_key)
        encrypted_age, signature_age = encrypt_data(age, quantum_key)
        encrypted_gender, signature_gender = encrypt_data(gender, quantum_key)
        encrypted_phone, signature_phone = encrypt_data(phone, quantum_key)
        encrypted_address, signature_address = encrypt_data(address, quantum_key)
        encrypted_disease_type, signature_disease = encrypt_data(disease_type, quantum_key)
        encrypted_image_path, image_signature = encrypt_image(original_image_path, quantum_key)
        
        '''print("Encrypted Name Size:", len(encrypted_name))
        print("Encrypted Age Size:", len(encrypted_age))
        print("Encrypted Gender Size:", len(encrypted_gender))
        print("Encrypted Phone Size:", len(encrypted_phone))
        print("Encrypted Address Size:", len(encrypted_address))
        print("Encrypted Disease Type Size:", len(encrypted_disease_type))
        print("Encrypted Image Path Size:", len(encrypted_image_path))'''
            
        cursor.execute("""
            INSERT INTO patient (name, age, gender, phone, address, disease_type, medical_image,did)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (encrypted_name, encrypted_age, encrypted_gender, encrypted_phone,
                encrypted_address, encrypted_disease_type, encrypted_image_path,int(did)))

        patient_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO signatures (name, age, gender, phone, address, diseasetype, img, pid)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (signature_name, signature_age, signature_gender, signature_phone,
                signature_address, signature_disease, image_signature, patient_id))
        con.commit()
            
        cursor.execute("select * from patientlogin where email='{}' and pid={}".format(email.strip(),int(patient_id)))
        pres = cursor.fetchall()
        password = random.randint(1000, 9999)
        subject="Your password and key"
        body="Hello user,\nGenerated password for your login is:"+str(password)+"\n\nYour key to view details:"+str(quantum_key)
        if pres==[]:
                
            cursor.execute("insert into patientlogin (email,password,pid) values ('{}','{}',{})".format(email.strip(),str(password).strip(),int(patient_id)))
            con.commit()
            mailing.mailsend(email.strip(),subject,body)
        else:
            mailing.mailsend(email.strip(),"Your Key For Decryption",str(quantum_key))
                
            
        cursor.execute("select * from user where id={} ".format(int(did)))
        dres = cursor.fetchall()
        demail=dres[0][1]
        dsubject = "Key to view patient details for patient id: "+str(patient_id)
        dbody = "patient id: "+str(patient_id)+"key: "+str(quantum_key)
        mailing.mailsend(demail,dsubject,dbody)
        flash(f"Data securely saved! Key for decryption: {quantum_key}", 'success')

    return render_template('radiologist_dashboard.html',res=res)

# Decrypt data with AES
def decrypt_data(encrypted_data, hex_key):
    key = bytes.fromhex(hex_key)
    iv = encrypted_data[:16]
    encrypted_content = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_content), AES.block_size)
    return decrypted_data.decode('utf-8')


# Decrypt image with AES
def decrypt_image(encrypted_image_path, hex_key):
    key = bytes.fromhex(hex_key)
    with open(encrypted_image_path, 'rb') as file:
        encrypted_image = file.read()

    iv = encrypted_image[:16]
    encrypted_content = encrypted_image[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_image_data = unpad(cipher.decrypt(encrypted_content), AES.block_size)
    return base64.b64encode(decrypted_image_data).decode('utf-8')


@app.route('/patdecryptdata', methods=['POST', 'GET'])
def patdecryptdata():
    if request.method == 'POST':
        patient_id = request.form.get('patientid')
        hex_key = request.form.get('key')

        if len(hex_key) != 32:
            flash("Invalid key length. Please use a 128-bit hexadecimal key.", 'danger')
            return redirect(url_for('patient_dashboard'))

        con = dbconnection()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM patient WHERE id=%s", (patient_id,))
        patient = cursor.fetchone()

        if not patient:
            flash("No data found for the provided patient ID.", 'danger')
            return render_template('pres.html')

        encrypted_name, encrypted_age, encrypted_gender, encrypted_phone, encrypted_address, encrypted_disease_type, encrypted_image_path,did = patient[1:]
        try:
            
            decrypted_name = decrypt_data(encrypted_name, hex_key)
            decrypted_age = decrypt_data(encrypted_age, hex_key)
            decrypted_gender = decrypt_data(encrypted_gender, hex_key)
            decrypted_phone = decrypt_data(encrypted_phone, hex_key)
            decrypted_address = decrypt_data(encrypted_address, hex_key)
            decrypted_disease_type = decrypt_data(encrypted_disease_type, hex_key)
            decrypted_image = decrypt_image(encrypted_image_path, hex_key)
        except:
            print("inside exception")
            flash("Invalid Key.", 'danger')
            return redirect(url_for('patient_dashboard'))
            

        return render_template(
            'pres.html',
            id=patient_id,
            name=decrypted_name,
            age=decrypted_age,
            gender=decrypted_gender,
            phone=decrypted_phone,
            address=decrypted_address,
            disease_type=decrypted_disease_type,
            image=decrypted_image
        )

    return redirect(url_for('patient_dashboard'))

@app.route('/docdecryptdata', methods=['POST', 'GET'])
def doc_decrypt_data():
    if request.method == 'POST':
        patient_id = request.form.get('patientid')
        hex_key = request.form.get('key')

        if len(hex_key) != 32:
            flash("Invalid key length. Please use a 128-bit hexadecimal key.", 'danger')
            return redirect(url_for('docdash'))

        con = dbconnection()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM patient WHERE id=%s", (patient_id,))
        patient = cursor.fetchone()

        if not patient:
            flash("No data found for the provided patient ID.", 'danger')
            return render_template('docres.html')

        encrypted_name, encrypted_age, encrypted_gender, encrypted_phone, encrypted_address, encrypted_disease_type, encrypted_image_path,did = patient[1:]
        try:
            
            decrypted_name = decrypt_data(encrypted_name, hex_key)
            decrypted_age = decrypt_data(encrypted_age, hex_key)
            decrypted_gender = decrypt_data(encrypted_gender, hex_key)
            decrypted_phone = decrypt_data(encrypted_phone, hex_key)
            decrypted_address = decrypt_data(encrypted_address, hex_key)
            decrypted_disease_type = decrypt_data(encrypted_disease_type, hex_key)
            decrypted_image = decrypt_image(encrypted_image_path, hex_key)
        except:
            print("inside exception")
            flash("Invalid Key.", 'danger')
            return redirect(url_for('docdash'))
            

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

    return redirect(url_for('docdash'))


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
        return jsonify({"verification Failed Data Tampered": False})
    
    
if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True)
