from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
config = {
    'user': 'mariadb',
    'password': '1234',
    'host': 'svc.sel5.cloudtype.app',
    'port': 31200,
    'database': 'mariadb'
}

def init_db():
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                content VARCHAR(255) NOT NULL,
                notes VARCHAR(255),
                group_code CHAR(4) NOT NULL
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()
    except Error as e:
        print("Error while connecting to MySQL", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    group_code = request.args.get('group_code', '')
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'POST' and 'save_group_code' not in request.form:
            date = request.form['date']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            content = request.form['content']
            notes = request.form['notes']
            group_code = request.args.get('group_code', '')

            # Convert input times to datetime objects
            start_time_dt = datetime.strptime(start_time, '%H:%M')
            end_time_dt = datetime.strptime(end_time, '%H:%M')

            if end_time_dt <= start_time_dt:
                return '''<script>alert("종료시간이 시작시간 보다도 작습니다."); window.location.href="/";</script>'''
            
            # Check for time conflicts
            cursor.execute('SELECT * FROM plans WHERE date = %s AND group_code = %s', (date, group_code))
            plans = cursor.fetchall()
            for plan in plans:
                plan_start_time = datetime.strptime(str(plan['start_time']), '%H:%M:%S')
                plan_end_time = datetime.strptime(str(plan['end_time']), '%H:%M:%S')
                if (start_time_dt < plan_end_time and end_time_dt > plan_start_time):
                    return '''<script>alert("시간이 중복 되었습니다."); window.location.href="/";</script>'''
            
            cursor.execute('INSERT INTO plans (date, start_time, end_time, content, notes, group_code) VALUES (%s, %s, %s, %s, %s, %s)', (date, start_time, end_time, content, notes, group_code))
            connection.commit()
            return redirect(url_for('index', group_code=group_code))
        
        cursor.execute('SELECT * FROM plans WHERE group_code = %s ORDER BY date, start_time', (group_code,))
        plans = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('index.html', plans=plans)
    
    except Error as e:
        print("Error while connecting to MySQL", e)
        return "Database connection error"

@app.route('/save_group_code', methods=['POST'])
def save_group_code():
    group_code = request.form['save_group_code']
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('SELECT COUNT(*) as count FROM plans WHERE group_code = %s', (group_code,))
        result = cursor.fetchone()
        
        if result and result.get('count', 0) > 0:
            cursor.close()
            connection.close()
            return '''<script>alert("다른 번호를 사용하세요."); window.location.href="/";</script>'''
        
        # Save group code (if unique) and redirect to the index with the new group code
        return redirect(url_for('index', group_code=group_code))
    
    except Error as e:
        print("Error while connecting to MySQL and querying:", e)
        return "Database connection error or query error"
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    group_code = request.args.get('group_code', '')
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        cursor.execute('DELETE FROM plans WHERE id = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index', group_code=group_code))
    
    except Error as e:
        print("Error while connecting to MySQL", e)
        return "Database connection error"

if __name__ == '__main__':
    init_db()
    try:
        app.run(host='0.0.0.0', debug=False)
    except Exception as e:
        print("An error occurred while running the server:", e)
