#
#   Created by Denny Pradipta
#   

#   Imports
from flask import Flask
from functools import wraps
import os, logging, random, string, datetime, json, bson, base64

from logging import Formatter, FileHandler
from flask import Flask, flash, request, jsonify, render_template,redirect,make_response,url_for,g,session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from pre_img import process_image
from models import *
from json_custom import *

#   Server Configuration
app = Flask(__name__)
app.secret_key = 'travelbasicsuksesbesar'
app.config['UPLOAD_FOLDER'] = './static/uploads/'
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
now = datetime.datetime.now().strftime("%d-%m-%Y")

if not app.debug:
	file_handler = FileHandler('error.log')
	file_handler.setFormatter(
		Formatter('%(asctime)s %(levelname)s: \
			%(message)s [in %(pathname)s:%(lineno)d]')
	)
	app.logger.setLevel(logging.INFO)
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)
	app.logger.info('errors')

#   Routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    if 'current_user' in session:
        g.user = session["current_user"]
    else:
        g.user = None

@app.route('/', methods=['GET', 'POST'])
def index():
	# Mengecek apakah ada akun admin
	is_admin_exists = Users.objects.count()
	# Jika metode GET...
	if request.method == 'GET':
		# Jika user sudah login, arahkan ke dasbor
		if 'current_user' in session:
			return redirect('/dashboard')
		else:
			# Jika ada akun admin, arahkan ke login 
			if(is_admin_exists > 0):
				return render_template(
					'login.html',
					title="Login"
				)
			else:
				# Jika tidak ada akun admin, arahkan ke registrasi 
				return render_template(
					'superadmin.html',
					title="Registrasi"
				)
	else:
		# Login
		if(is_admin_exists > 0):
			username = request.form['username']
			password = request.form['password']
			user_data = Users.objects.get(username=username)
			if check_password_hash(user_data.password, password):
				session['current_user'] = user_data.username
				g.user = user_data.username
				return redirect('/dashboard')
			else:
				flash('Mohon periksa kembali data yang dimasukkan!', 'danger')
				return redirect('/')

		else:
			#Daftar
			username = request.form['username']
			password = generate_password_hash(request.form['password'])
			user_data = Users(username, password, "superadmin")

			if user_data.save():
				flash('Anda telah berhasil mendaftarkan akun super admin!', 'success')
				return redirect('/')
			else:
				flash('Pendaftaran gagal', 'danger')
				return redirect('/')

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
	return render_template(
		'index.html',
		title="Index"
	)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
	if request.method == 'POST':
		print(request.form['issuecheck'])
		print(request.form['nationcheck'])
		try:
			passport_num = request.form['passport_num'].upper()
			name = request.form['name'].upper()
			issue = request.form['nation'].upper()
			issue_n = request.form['issuecheck'].upper()
			nation = request.form['nation'].upper()
			nation_n = request.form['nationcheck'].upper()
			birth_date = datetime.datetime.strptime(request.form['birthdate'], '%d/%m/%Y')
			sex = request.form['sex'].upper()
			expirydate = datetime.datetime.strptime(request.form['expirydate'], '%d/%m/%Y')
			image = request.form['passport_image']
			image_path = request.form['passport_path']

			passport = Passports(passport_num, name, issue, issue_n, nation, nation_n, birth_date, 
				sex, expirydate, image, image_path)

			if passport.save():
				flash('Data milik {} telah berhasil diinput!'.format(name), 'success')
				return redirect('/')
			else:
				flash('Mohon cek kembali data yang diinput!', 'danger')
				return render_template(
					'upload.html',
					title="Error"
				)
		except Exception as e:
			flash(
				'Terjadi kesalahan pada data yang diinput. Mohon perhatikan dengan baik data yang diinput!<br>' +
				'Error disebabkan karena: {}'.format(e), 
				'danger')
			return redirect('/upload')
	else:
		return render_template('upload.html',
			title="Upload")

@app.route('/reports', methods=['GET'])
@login_required
def reports():
	return render_template(
		'reports.html',
		title="Reports"
	)

@app.route('/edit/<data_id>', methods=['GET', 'POST'])
@login_required
def edit(data_id):
	if request.method == 'POST':
		try:
			passport_num = request.form['passport_num'].upper()
			name = request.form['name'].upper()
			issue = request.form['issue'].upper()
			issue_n = request.form['issuecheck'].upper()
			nation = request.form['nation'].upper()
			nation_n = request.form['nationcheck'].upper()
			birth_date = datetime.datetime.strptime(request.form['birthdate'], '%d/%m/%Y')
			sex = request.form['sex'].upper()
			expirydate = datetime.datetime.strptime(request.form['expirydate'], '%d/%m/%Y')
			image = request.form['passport_image']
			image_path = request.form['passport_path']

			if Passports.objects(id=data_id).update(
				passport_num=passport_num, 
				name=name, 
				issue=issue,
				issue_n=issue_n,
				nation=nation,
				nation_n=nation_n,
				birthdate=birth_date, 
				sex=sex, 
				expirydate=expirydate, 
				image=image, 
				image_path=image_path,
				modified_at=datetime.datetime.now()
			):
				flash('Data milik {} telah berhasil diedit!'.format(name), 'success')
				return redirect('/dashboard')
			else:
				flash('Mohon cek kembali data yang diinput!', 'danger')
				return redirect('/edit/{}'.format(data_id))
		except Exception as e:
			flash(
				'Terjadi kesalahan pada data yang diinput. Mohon perhatikan dengan baik data yang diinput!<br>' +
				'Error disebabkan karena: {}'.format(e), 
				'danger')
			return redirect('/edit/{}'.format(data_id))

	else:
		passport_data = bson.json_util.loads(Passports.objects.get(id=data_id).to_json())
		return render_template(
			'edit.html',
			title="Edit",
			data=passport_data
		)

@app.route('/delete/<data_id>', methods=['GET'])
@login_required
def delete(data_id):
	# Mencari data dengan id = parameter
	passport_data = Passports.objects.get(id=data_id)
	# Hapus data
	passport_data.delete()
	flash('Data berhasil dihapus!', 'success')
	return redirect('/')

@app.route('/logout')
def logout():
    session.pop('current_user', None)
    g.user = None
    return redirect(url_for('index'))

#   API Routes
@app.route('/api/upload/upload', methods=['POST'])
@login_required
def api_upload():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			extension = os.path.splitext(file.filename)[1].lower()
			image = secure_filename(random_name(16))+extension
			if not os.path.exists(app.config['UPLOAD_FOLDER']+now):
				os.makedirs(app.config['UPLOAD_FOLDER']+now)
			file.save(os.path.join(app.config['UPLOAD_FOLDER']+now, image))
			path="static/uploads/{}/{}".format(now, image)
			print ("File original {} telah diupload ".format(path))
			return json_response({
				"success": "true",
				"path": path,
				"image": image,
				"message": "Sukses mengupload file."
			}, cls=JSONEncoder)
		else:
			return json_response({
				"success": "false",
				"message": "Terjadi kesalahan saat mengupload gambar. Mohon untuk mengulang kembali."
			})
	else:
		return jsonify({
			"error": "Harap hubungi administrator!",
			"success": "false"
		})

@app.route('/api/upload/process', methods=['POST'])
@login_required
def api_process():
	if request.method == 'POST':
		jsonData = request.get_json()
		imageBlob = jsonData['image'].partition(",")[2]
		os.remove("static/uploads/{}/{}".format(now, jsonData['fileName']))
		with open("static/uploads/{}/resized_{}".format(now, jsonData['fileName']), "wb") as fh:
			fh.write(base64.decodebytes(imageBlob.encode()))
			image = jsonData['fileName']
			path = "static/uploads/{}/resized_{}".format(now, jsonData['fileName'])
			print ("File telah dicrop dan disimpan dalam {}".format(path))
			rec_string = process_image(path=path, name=jsonData['fileName'])
			if(rec_string):
				return json_response({
					"output": rec_string,
					"path": path,
					"image": image,
					"success": "true",
					"message": "Pembacaan sukses."
				}, cls=JSONEncoder)
			else:
				return json_response({
					"output": rec_string,
					"path": path,
					"image": image,
					"success": "false",
					"message": "Pembacaan gagal."
				}, cls=JSONEncoder)
	else:
		return jsonify({
			"error": "Harap hubungi administrator!",
			"success": "false"
		})

@app.route('/api/manage', methods=['GET'])
@login_required
def api_manage():
	# Memberikan semua data paspor
	results = bson.json_util.loads(Passports.objects.order_by('name').to_json())
	return json_response({
		"output": results
	}, cls=JSONEncoder)

@app.route('/api/report/<date_from>/<date_to>')
@login_required
def api_report(date_from, date_to):
	query = bson.json_util.loads(Passports.objects(Q(created_at__gt=date_from) & Q(created_at__lte=date_to))
		.order_by('name')
		.to_json())
	return json_response({
		"results": query,
		"date_from": request.args.get('date_from'),
		"date_to": request.args.get('date_to')}, cls=JSONEncoder)

#   Error Handlers 
@app.errorhandler(500)
def internal_error(error):
	print(str(error))  # ghetto logging

@app.errorhandler(404)
def not_found_error(error):
	print(str(error))

@app.errorhandler(405)
def not_allowed_error(error):
	print(str(error))

#   Functions
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def random_name(length):
   letters = string.ascii_lowercase + string.digits + string.ascii_uppercase 
   return ''.join(random.choice(letters) for i in range(length))