import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'visitors.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class VisitorLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(100), default='Unknown')
    country_code = db.Column(db.String(10), default='PH')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/track', methods=['POST'])
def track_visitor():
    data = request.get_json() or {}
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    country = data.get('country', 'Philippines')
    country_code = data.get('country_code', 'PH')

    new_log = VisitorLog(ip_address=ip, country=country, country_code=country_code)
    db.session.add(new_log)
    db.session.commit()

    total_views = VisitorLog.query.count() + 1420

    country_stats = {}
    for log in VisitorLog.query.all():
        code = log.country_code or 'PH'
        country_stats[code] = country_stats.get(code, 0) + 1
    
    default_stats = {"PH": 890, "US": 215, "CA": 94, "GB": 62, "AE": 45}
    for k, v in default_stats.items():
        country_stats[k] = country_stats.get(k, 0) + v

    return jsonify({
        'total_views': total_views,
        'country_stats': country_stats,
        'your_country': country_code
    })

if __name__ == '__main__':
    app.run(debug=True)