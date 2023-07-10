from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import re


app = Flask(__name__, template_folder='template')
app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=824dfd4d-99de-440d-9991-629c01b3832d.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30119;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA (2).crt;UID=gzt33282;PWD=Ufsj8ideWJk2J3QX", '', '')
print("connected")


@app.route("/", methods=['POST', 'GET'])
def login():
    global Userid
    msg = ''

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM userdata WHERE EMAIL=? AND PASSWORD=?"  # from db2 sql table
        stmt = ibm_db.prepare(conn, sql)
        # this username & password is should be same as db-2 details & order also
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['Loggedin'] = True
            session['id'] = account['EMAIL']
            Userid = account['EMAIL']
            session['email'] = account['EMAIL']
            msg = "logged in successfully !"
            return render_template('home.html', msg=msg, user=email)
        else:
            msg = "Incorrect Email/password"
    return render_template('login.html', msg=msg)


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    msg = ''
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT* FROM userdata WHERE name= ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, name)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            return render_template('signup.html', error= True)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid Email Address!"
        else:
            insert_sql = "INSERT INTO userdata VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            # this username & password is should be same as db-2 details & order also
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
            msg = "You have successfully registered !"
    return render_template('signup.html', msg=msg)


@app.route("/home", methods=["POST", "GET"])
def home():
       
    if(request.method == "POST"):
        LAT = request.form["lat"]
        LONG = request.form["lon"]
        VISITED = 0
        if(LAT == "" or LONG == ""):
            return render_template('home.html', success=0)
        else:
            insert_sql = "INSERT INTO locationdata VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, LAT)
            ibm_db.bind_param(prep_stmt, 2, LONG)
            ibm_db.bind_param(prep_stmt, 3, VISITED)
            ibm_db.execute(prep_stmt)
            return render_template('home.html', success=True )
    return render_template('home.html')    
      
    
@app.route('/data')
def data():

    finaldata = []
    sql = "SELECT * FROM locationdata"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_assoc(stmt)

    while dictionary != False:
        location = []
        location.append(dictionary["LAT"])
        location.append(dictionary["LONG"])
        location.append(dictionary["VISITED"])
        finaldata.append(location)
        print(location)
        dictionary = ibm_db.fetch_assoc(stmt)
    print(finaldata)
    return render_template('data.html', responses=finaldata)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)





