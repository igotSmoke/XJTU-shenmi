from flask import Flask, request, jsonify
from flask_cors import CORS
from database import execute_query
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 启用CORS

# 车队相关接口
@app.route('/fleets/', methods=['GET'])
def get_fleets():
    result = execute_query('SELECT * FROM fleet')
    return jsonify(result)

@app.route('/fleets/', methods=['POST'])
def create_fleet():
    data = request.get_json()
    result = execute_query(
        'INSERT INTO fleet (name) VALUES (%s) RETURNING fleet_id',
        (data['name'],)
    )
    return jsonify({'fleet_id': result[0]['fleet_id']}), 201

@app.route('/fleets/<int:fleet_id>', methods=['PUT'])
def update_fleet(fleet_id):
    data = request.get_json()
    execute_query(
        'UPDATE fleet SET name = %s WHERE fleet_id = %s',
        (data['name'], fleet_id)
    )
    return jsonify({'message': '更新成功'})

@app.route('/fleets/<int:fleet_id>', methods=['DELETE'])
def delete_fleet(fleet_id):
    execute_query('DELETE FROM fleet WHERE fleet_id = %s', (fleet_id,))
    return jsonify({'message': '删除成功'})

# 车辆相关接口
@app.route('/vehicles/', methods=['GET'])
def get_vehicles():
    result = execute_query('SELECT * FROM vehicle')
    return jsonify(result)

@app.route('/vehicles/', methods=['POST'])
def create_vehicle():
    data = request.get_json()
    execute_query(
        'INSERT INTO vehicle (license_plate, manufacturer, production_date, fleet_id) VALUES (%s, %s, %s, %s)',
        (data['license_plate'], data['manufacturer'], data['production_date'], data['fleet_id'])
    )
    return jsonify({'message': '添加成功'}), 201

@app.route('/vehicles/<license_plate>', methods=['PUT'])
def update_vehicle(license_plate):
    data = request.get_json()
    execute_query(
        'UPDATE vehicle SET manufacturer = %s, production_date = %s, fleet_id = %s WHERE license_plate = %s',
        (data['manufacturer'], data['production_date'], data['fleet_id'], license_plate)
    )
    return jsonify({'message': '更新成功'})

@app.route('/vehicles/<license_plate>', methods=['DELETE'])
def delete_vehicle(license_plate):
    execute_query('DELETE FROM vehicle WHERE license_plate = %s', (license_plate,))
    return jsonify({'message': '删除成功'})

# 司机相关接口
@app.route('/drivers/', methods=['GET'])
def get_drivers():
    result = execute_query('SELECT * FROM driver')
    return jsonify(result)

@app.route('/drivers/', methods=['POST'])
def create_driver():
    data = request.get_json()
    result = execute_query(
        'INSERT INTO driver (name, phone, fleet_id, hire_period) VALUES (%s, %s, %s, %s) RETURNING driver_id',
        (data['name'], data['phone'], data['fleet_id'], data['hire_period'])
    )
    return jsonify({'driver_id': result[0]['driver_id']}), 201

@app.route('/drivers/<int:driver_id>', methods=['PUT'])
def update_driver(driver_id):
    data = request.get_json()
    execute_query(
        'UPDATE driver SET name = %s, phone = %s, fleet_id = %s, hire_period = %s WHERE driver_id = %s',
        (data['name'], data['phone'], data['fleet_id'], data['hire_period'], driver_id)
    )
    return jsonify({'message': '更新成功'})

@app.route('/drivers/<int:driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    execute_query('DELETE FROM driver WHERE driver_id = %s', (driver_id,))
    return jsonify({'message': '删除成功'})

# 驾驶记录相关接口
@app.route('/drives/', methods=['GET'])
def get_drives():
    result = execute_query('SELECT * FROM drive')
    return jsonify(result)

@app.route('/drives/', methods=['POST'])
def create_drive():
    data = request.get_json()
    execute_query(
        'INSERT INTO drive (driver_id, license_plate, drive_date, mileage) VALUES (%s, %s, %s, %s)',
        (data['driver_id'], data['license_plate'], data['drive_date'], data['mileage'])
    )
    return jsonify({'message': '添加成功'}), 201

@app.route('/drives/<int:driver_id>/<license_plate>/<drive_date>', methods=['PUT'])
def update_drive(driver_id, license_plate, drive_date):
    data = request.get_json()
    execute_query(
        'UPDATE drive SET mileage = %s WHERE driver_id = %s AND license_plate = %s AND drive_date = %s',
        (data['mileage'], driver_id, license_plate, drive_date)
    )
    return jsonify({'message': '更新成功'})

@app.route('/drives/<int:driver_id>/<license_plate>/<drive_date>', methods=['DELETE'])
def delete_drive(driver_id, license_plate, drive_date):
    execute_query(
        'DELETE FROM drive WHERE driver_id = %s AND license_plate = %s AND drive_date = %s',
        (driver_id, license_plate, drive_date)
    )
    return jsonify({'message': '删除成功'})

if __name__ == '__main__':
    app.run(debug=True) 