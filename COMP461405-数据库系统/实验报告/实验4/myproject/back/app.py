from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import Error
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 数据库连接配置
DB_CONFIG = {
    'dbname': 'db44',
    'user': 'user44',
    'password': 'user44_password',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    try:
        print("尝试连接数据库...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("数据库连接成功！")
        return conn
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None

# 车队相关接口
@app.route('/api/fleet', methods=['GET'])
def get_fleets():
    print("收到获取车队列表请求")
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM fleet")
            fleets = cur.fetchall()
            print(f"查询到 {len(fleets)} 个车队")
            cur.close()
            conn.close()
            return jsonify([{'fleet_id': f[0], 'name': f[1]} for f in fleets])
        except Error as e:
            print(f"查询车队数据错误: {e}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/fleet', methods=['POST'])
def add_fleet():
    print("收到添加车队请求")
    data = request.json
    print(f"请求数据: {data}")
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO fleet (name) VALUES (%s) RETURNING fleet_id", (data['name'],))
            fleet_id = cur.fetchone()[0]
            conn.commit()
            print(f"成功添加车队，ID: {fleet_id}")
            cur.close()
            conn.close()
            return jsonify({'fleet_id': fleet_id, 'name': data['name']})
        except Error as e:
            print(f"添加车队错误: {e}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/fleet/<int:fleet_id>', methods=['PUT'])
def update_fleet(fleet_id):
    print(f"收到修改车队请求，ID: {fleet_id}")
    data = request.json
    print(f"请求数据: {data}")
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("UPDATE fleet SET name = %s WHERE fleet_id = %s RETURNING fleet_id", 
                       (data['name'], fleet_id))
            if cur.rowcount == 0:
                return jsonify({'error': '车队不存在'}), 404
            conn.commit()
            print(f"成功修改车队，ID: {fleet_id}")
            cur.close()
            conn.close()
            return jsonify({'fleet_id': fleet_id, 'name': data['name']})
        except Error as e:
            print(f"修改车队错误: {e}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/fleet/<int:fleet_id>', methods=['DELETE'])
def delete_fleet(fleet_id):
    print(f"收到删除车队请求，ID: {fleet_id}")
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # 首先检查是否有相关的车辆或驾驶员
            cur.execute("SELECT COUNT(*) FROM vehicle WHERE fleet_id = %s", (fleet_id,))
            vehicle_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM driver WHERE fleet_id = %s", (fleet_id,))
            driver_count = cur.fetchone()[0]
            
            if vehicle_count > 0 or driver_count > 0:
                return jsonify({'error': '该车队下还有车辆或驾驶员，无法删除'}), 400
            
            cur.execute("DELETE FROM fleet WHERE fleet_id = %s", (fleet_id,))
            if cur.rowcount == 0:
                return jsonify({'error': '车队不存在'}), 404
            conn.commit()
            print(f"成功删除车队，ID: {fleet_id}")
            cur.close()
            conn.close()
            return jsonify({'message': '删除成功'})
        except Error as e:
            print(f"删除车队错误: {e}")
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

# 车辆相关接口
@app.route('/api/vehicle', methods=['GET'])
def get_vehicles():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM vehicle")
            vehicles = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify([{
                'license_plate': v[0],
                'manufacturer': v[1],
                'production_date': v[2].strftime('%Y-%m-%d') if v[2] else None,
                'fleet_id': v[3]
            } for v in vehicles])
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/vehicle', methods=['POST'])
def add_vehicle():
    data = request.json
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO vehicle (license_plate, manufacturer, production_date, fleet_id) VALUES (%s, %s, %s, %s)",
                (data['license_plate'], data['manufacturer'], data['production_date'], data['fleet_id'])
            )
            conn.commit()
            cur.close()
            conn.close()
            return jsonify(data)
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/vehicle/<license_plate>', methods=['PUT'])
def update_vehicle(license_plate):
    data = request.json
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE vehicle SET manufacturer = %s, production_date = %s, fleet_id = %s WHERE license_plate = %s",
                (data['manufacturer'], data['production_date'], data['fleet_id'], license_plate)
            )
            if cur.rowcount == 0:
                return jsonify({'error': '车辆不存在'}), 404
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({**data, 'license_plate': license_plate})
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/vehicle/<license_plate>', methods=['DELETE'])
def delete_vehicle(license_plate):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # 检查是否有相关的驾驶记录
            cur.execute("SELECT COUNT(*) FROM drive WHERE license_plate = %s", (license_plate,))
            drive_count = cur.fetchone()[0]
            
            if drive_count > 0:
                return jsonify({'error': '该车辆还有驾驶记录，无法删除'}), 400
            
            cur.execute("DELETE FROM vehicle WHERE license_plate = %s", (license_plate,))
            if cur.rowcount == 0:
                return jsonify({'error': '车辆不存在'}), 404
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'message': '删除成功'})
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

# 驾驶员相关接口
@app.route('/api/driver', methods=['GET'])
def get_drivers():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM driver")
            drivers = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify([{
                'driver_id': d[0],
                'name': d[1],
                'phone': d[2],
                'fleet_id': d[3],
                'hire_period': d[4]
            } for d in drivers])
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/driver', methods=['POST'])
def add_driver():
    data = request.json
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO driver (name, phone, fleet_id, hire_period) VALUES (%s, %s, %s, %s) RETURNING driver_id",
                (data['name'], data['phone'], data['fleet_id'], data['hire_period'])
            )
            driver_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({**data, 'driver_id': driver_id})
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/driver/<int:driver_id>', methods=['PUT'])
def update_driver(driver_id):
    data = request.json
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE driver SET name = %s, phone = %s, fleet_id = %s, hire_period = %s WHERE driver_id = %s",
                (data['name'], data['phone'], data['fleet_id'], data['hire_period'], driver_id)
            )
            if cur.rowcount == 0:
                return jsonify({'error': '驾驶员不存在'}), 404
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({**data, 'driver_id': driver_id})
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/driver/<int:driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # 检查是否有相关的驾驶记录
            cur.execute("SELECT COUNT(*) FROM drive WHERE driver_id = %s", (driver_id,))
            drive_count = cur.fetchone()[0]
            
            if drive_count > 0:
                return jsonify({'error': '该驾驶员还有驾驶记录，无法删除'}), 400
            
            cur.execute("DELETE FROM driver WHERE driver_id = %s", (driver_id,))
            if cur.rowcount == 0:
                return jsonify({'error': '驾驶员不存在'}), 404
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'message': '删除成功'})
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

# 驾驶记录相关接口
@app.route('/api/drive', methods=['GET'])
def get_drives():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM drive")
            drives = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify([{
                'driver_id': d[0],
                'license_plate': d[1],
                'drive_date': d[2].strftime('%Y-%m-%d'),
                'mileage': d[3]
            } for d in drives])
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/drive', methods=['POST'])
def add_drive():
    data = request.json
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO drive (driver_id, license_plate, drive_date, mileage) VALUES (%s, %s, %s, %s)",
                (data['driver_id'], data['license_plate'], data['drive_date'], data['mileage'])
            )
            conn.commit()
            cur.close()
            conn.close()
            return jsonify(data)
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

@app.route('/api/drive', methods=['DELETE'])
def delete_drive():
    data = request.json
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM drive WHERE driver_id = %s AND license_plate = %s AND drive_date = %s",
                (data['driver_id'], data['license_plate'], data['drive_date'])
            )
            if cur.rowcount == 0:
                return jsonify({'error': '驾驶记录不存在'}), 404
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'message': '删除成功'})
        except Error as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': '数据库连接失败'}), 500

if __name__ == '__main__':
    print("启动Flask应用...")
    app.run(debug=True, port=5000) 