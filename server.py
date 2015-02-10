from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from flask import redirect
from flask import jsonify
from flask import session
from flask import flash
import hashlib, binascii
import sqlite3

app = Flask(__name__)

conn = None

# Get the current connection
def get_conn():
	global conn
	if conn is None:
		conn = sqlite3.connect('database.sql')
		# Dictionary results
		conn.row_factory = sqlite3.Row
	return conn

# Close the connection 
def close_connection():
	global conn
	if conn is not None:
		conn.close()

# Query the database from the connection
def query_db(query, args=(), one=False):
	cur = get_conn().cursor()
	cur.execute(query, args)
	r = cur.fetchall()
	cur.close()
	return (r[0] if r else None) if one else r

# Add a task to the database
def add_task(category, priority, description):
	query_db('INSERT INTO tasks values(?, ?, ?)', (category, priority, description), one=True)
	get_conn().commit()

# Delete task from database
def delete_task(rowid):
	query_db('DELETE FROM tasks WHERE rowid=(?)', (rowid))
	get_conn().commit()

#Valid the username and password
def validate(username, password):
	#Used as a smaller substitute, as in comparison to SHA256 or SHA512
	dk = hashlib.new('ripemd160')
	dk.update(password)
	password = dk.hexdigest()
	return query_db('SELECT * from users where username=(?) and password=(?)', (username, password), one=True)
	

#Adding and getting tasks
@app.route('/', methods=['GET', 'POST'])
def tasks():
	if request.method == "POST" and 'logged_in' in session:
		category = request.form['category']
		priority = request.form['priority']
		description = request.form['description']
		add_task(category, priority, description)
		flash('New task was successfully added')
		return redirect(url_for('tasks'))
	else:
		tasks = query_db('SELECT rowid, * FROM tasks ORDER BY priority DESC')
		return render_template('index.html', tasks=tasks)

#Logging in
@app.route('/login', methods=['POST'])
def login():
	username = request.form['username']
	password = request.form['password']
	if (validate(username, password)):
		session['logged_in'] = True
		flash("Login Successful")
	else:
		flash('Error: Invalid Password')	
	return redirect(url_for('tasks'))

# Logout, clear session information
@app.route('/logout', methods=['GET'])
def logout():
	session.clear()
	return redirect(url_for('tasks'))

# Delete a task
@app.route('/delete', methods=['POST'])
def delete():
	if 'logged_in' in session and session['logged_in']:
		rowid = request.form['rowid']
		delete_task(rowid)
		flash('Deleted task successfully')
		return jsonify({'status': True})
	else:
		return jsonify({'status': False})

if __name__ == "__main__":
	
	# Really lame keys and startup
	app.secret_key = 'something really secret'
	app.config['SESSION_TYPE'] = 'filesystem'
	app.debug = True
	app.run()
