from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
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

app.config['MYSQL_HOST'] = config['host']
app.config['MYSQL_USER'] = config['user']
app.config['MYSQL_PASSWORD'] = config['password']
app.config['MYSQL_DB'] = config['database']
app.config['MYSQL_PORT'] = config['port']

mysql = MySQL(app)

def init_db():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            content VARCHAR(255) NOT NULL,
            notes VARCHAR(255)
        )
    """)
    mysql.connection.commit()
    cursor.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        content = request.form['content']
        notes = request.form['notes']

        # Convert input times to datetime objects
        start_time_dt = datetime.strptime(start_time, '%H:%M')
        end_time_dt = datetime.strptime(end_time, '%H:%M')

        if end_time_dt <= start_time_dt:
            return '''<script>alert("종료시간이 시작시간 보다도 작습니다."); window.location.href="/";</script>'''
        
        # Check for time conflicts
        cursor.execute('SELECT * FROM plans WHERE date = %s', (date,))
        plans = cursor.fetchall()
        for plan in plans:
            plan_start_time = datetime.strptime(str(plan['start_time']), '%H:%M:%S')
            plan_end_time = datetime.strptime(str(plan['end_time']), '%H:%M:%S')
            if (start_time_dt < plan_end_time and end_time_dt > plan_start_time):
                return '''<script>alert("시간이 중복 되었습니다."); window.location.href="/";</script>'''
        
        cursor.execute('INSERT INTO plans (date, start_time, end_time, content, notes) VALUES (%s, %s, %s, %s, %s)', (date, start_time, end_time, content, notes))
        mysql.connection.commit()
        return redirect(url_for('index'))
    
    cursor.execute('SELECT * FROM plans ORDER BY date, start_time')
    plans = cursor.fetchall()
    cursor.close()
    return render_template('index.html', plans=plans)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM plans WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
