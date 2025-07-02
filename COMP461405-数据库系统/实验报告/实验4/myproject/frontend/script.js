// 全局变量
const API_BASE_URL = 'http://localhost:5000/api';

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    // 加载所有数据
    loadFleets();
    loadVehicles();
    loadDrivers();
    loadDriveRecords();

    // 设置表单提交事件
    document.getElementById('fleetForm').addEventListener('submit', addFleet);
    document.getElementById('vehicleForm').addEventListener('submit', addVehicle);
    document.getElementById('driverForm').addEventListener('submit', addDriver);
    document.getElementById('driveForm').addEventListener('submit', addDriveRecord);

    // 设置修改表单提交事件
    document.getElementById('editFleetForm').addEventListener('submit', modifyFleet);
    document.getElementById('editVehicleForm').addEventListener('submit', modifyVehicle);
    document.getElementById('editDriverForm').addEventListener('submit', modifyDriver);

    // 设置模态框关闭事件
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.style.display = 'none';
            });
        });
    });

    // 点击模态框外部关闭
    window.addEventListener('click', (event) => {
        document.querySelectorAll('.modal').forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
});

// 显示指定部分
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
    
    // 根据显示的部分加载相应的选项
    if (sectionId === 'drive') {
        loadDriverOptions();
        loadVehicleOptions();
    }
}

// 加载车队列表
async function loadFleets() {
    try {
        const response = await fetch(`${API_BASE_URL}/fleet`);
        const fleets = await response.json();
        const tbody = document.querySelector('#fleetTable tbody');
        tbody.innerHTML = '';
        
        fleets.forEach(fleet => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${fleet.fleet_id}</td>
                <td>${fleet.name}</td>
                <td>
                    <button onclick="showEditFleetModal(${fleet.fleet_id}, '${fleet.name}')" class="edit-btn">修改</button>
                    <button onclick="deleteFleet(${fleet.fleet_id})" class="delete-btn">删除</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // 更新车队选择框
        updateFleetSelects();
    } catch (error) {
        console.error('加载车队失败:', error);
        alert('加载车队失败');
    }
}

// 加载车辆列表
async function loadVehicles() {
    try {
        const response = await fetch(`${API_BASE_URL}/vehicle`);
        const vehicles = await response.json();
        const tbody = document.querySelector('#vehicleTable tbody');
        tbody.innerHTML = '';
        
        vehicles.forEach(vehicle => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${vehicle.license_plate}</td>
                <td>${vehicle.manufacturer}</td>
                <td>${vehicle.production_date}</td>
                <td>${vehicle.fleet_id}</td>
                <td>
                    <button onclick="showEditVehicleModal('${vehicle.license_plate}', '${vehicle.manufacturer}', '${vehicle.production_date}', ${vehicle.fleet_id})" class="edit-btn">修改</button>
                    <button onclick="deleteVehicle('${vehicle.license_plate}')" class="delete-btn">删除</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('加载车辆失败:', error);
        alert('加载车辆失败');
    }
}

// 加载驾驶员列表
async function loadDrivers() {
    try {
        const response = await fetch(`${API_BASE_URL}/driver`);
        const drivers = await response.json();
        const tbody = document.querySelector('#driverTable tbody');
        tbody.innerHTML = '';
        
        drivers.forEach(driver => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${driver.driver_id}</td>
                <td>${driver.name}</td>
                <td>${driver.phone}</td>
                <td>${driver.fleet_id}</td>
                <td>${driver.hire_period}</td>
                <td>
                    <button onclick="showEditDriverModal(${driver.driver_id}, '${driver.name}', '${driver.phone}', ${driver.fleet_id}, '${driver.hire_period}')" class="edit-btn">修改</button>
                    <button onclick="deleteDriver(${driver.driver_id})" class="delete-btn">删除</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('加载驾驶员失败:', error);
        alert('加载驾驶员失败');
    }
}

// 加载驾驶记录列表
async function loadDriveRecords() {
    try {
        const response = await fetch(`${API_BASE_URL}/drive`);
        const records = await response.json();
        const tbody = document.querySelector('#driveTable tbody');
        tbody.innerHTML = '';
        
        records.forEach(record => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${record.driver_id}</td>
                <td>${record.license_plate}</td>
                <td>${record.drive_date}</td>
                <td>${record.mileage}</td>
                <td>
                    <button onclick="deleteDriveRecord(${record.driver_id}, '${record.license_plate}', '${record.drive_date}')" class="delete-btn">删除</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('加载驾驶记录失败:', error);
        alert('加载驾驶记录失败');
    }
}

// 更新所有车队选择框
async function updateFleetSelects() {
    try {
        const response = await fetch(`${API_BASE_URL}/fleet`);
        const fleets = await response.json();
        
        const selects = [
            document.getElementById('fleetId'),
            document.getElementById('driverFleetId'),
            document.getElementById('editFleetId'),
            document.getElementById('editDriverFleetId')
        ];

        selects.forEach(select => {
            if (select) {
                select.innerHTML = '';
                fleets.forEach(fleet => {
                    const option = document.createElement('option');
                    option.value = fleet.fleet_id;
                    option.textContent = fleet.name;
                    select.appendChild(option);
                });
            }
        });
    } catch (error) {
        console.error('更新车队选择框失败:', error);
    }
}

// 显示修改车队模态框
function showEditFleetModal(id, name) {
    document.getElementById('editFleetId').value = id;
    document.getElementById('editFleetName').value = name;
    document.getElementById('editFleetModal').style.display = 'block';
}

// 显示修改车辆模态框
function showEditVehicleModal(licensePlate, manufacturer, productionDate, fleetId) {
    document.getElementById('editLicensePlate').value = licensePlate;
    document.getElementById('editManufacturer').value = manufacturer;
    document.getElementById('editProductionDate').value = productionDate;
    document.getElementById('editFleetId').value = fleetId;
    document.getElementById('editVehicleModal').style.display = 'block';
}

// 显示修改驾驶员模态框
function showEditDriverModal(id, name, phone, fleetId, hirePeriod) {
    document.getElementById('editDriverId').value = id;
    document.getElementById('editDriverName').value = name;
    document.getElementById('editDriverPhone').value = phone;
    document.getElementById('editDriverFleetId').value = fleetId;
    document.getElementById('editHirePeriod').value = hirePeriod;
    document.getElementById('editDriverModal').style.display = 'block';
}

// 修改车队
async function modifyFleet(event) {
    event.preventDefault();
    const id = document.getElementById('editFleetId').value;
    const name = document.getElementById('editFleetName').value;

    try {
        const response = await fetch(`${API_BASE_URL}/fleet/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name })
        });

        if (response.ok) {
            document.getElementById('editFleetModal').style.display = 'none';
            loadFleets();
        } else {
            const error = await response.json();
            alert(error.message || '修改车队失败');
        }
    } catch (error) {
        console.error('修改车队失败:', error);
        alert('修改车队失败');
    }
}

// 修改车辆
async function modifyVehicle(event) {
    event.preventDefault();
    const licensePlate = document.getElementById('editLicensePlate').value;
    const vehicle = {
        manufacturer: document.getElementById('editManufacturer').value,
        production_date: document.getElementById('editProductionDate').value,
        fleet_id: document.getElementById('editFleetId').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/vehicle/${licensePlate}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(vehicle)
        });

        if (response.ok) {
            document.getElementById('editVehicleModal').style.display = 'none';
            loadVehicles();
        } else {
            const error = await response.json();
            alert(error.message || '修改车辆失败');
        }
    } catch (error) {
        console.error('修改车辆失败:', error);
        alert('修改车辆失败');
    }
}

// 修改驾驶员
async function modifyDriver(event) {
    event.preventDefault();
    const id = document.getElementById('editDriverId').value;
    const driver = {
        name: document.getElementById('editDriverName').value,
        phone: document.getElementById('editDriverPhone').value,
        fleet_id: document.getElementById('editDriverFleetId').value,
        hire_period: document.getElementById('editHirePeriod').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/driver/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(driver)
        });

        if (response.ok) {
            document.getElementById('editDriverModal').style.display = 'none';
            loadDrivers();
        } else {
            const error = await response.json();
            alert(error.message || '修改驾驶员失败');
        }
    } catch (error) {
        console.error('修改驾驶员失败:', error);
        alert('修改驾驶员失败');
    }
}

// 删除车队
async function deleteFleet(id) {
    if (!confirm('确定要删除这个车队吗？')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/fleet/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadFleets();
        } else {
            const error = await response.json();
            alert(error.message || '删除车队失败');
        }
    } catch (error) {
        console.error('删除车队失败:', error);
        alert('删除车队失败');
    }
}

// 删除车辆
async function deleteVehicle(licensePlate) {
    if (!confirm('确定要删除这辆车吗？')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/vehicle/${licensePlate}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadVehicles();
        } else {
            const error = await response.json();
            alert(error.message || '删除车辆失败');
        }
    } catch (error) {
        console.error('删除车辆失败:', error);
        alert('删除车辆失败');
    }
}

// 删除驾驶员
async function deleteDriver(id) {
    if (!confirm('确定要删除这个驾驶员吗？')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/driver/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadDrivers();
        } else {
            const error = await response.json();
            alert(error.message || '删除驾驶员失败');
        }
    } catch (error) {
        console.error('删除驾驶员失败:', error);
        alert('删除驾驶员失败');
    }
}

// 删除驾驶记录
async function deleteDriveRecord(driverId, licensePlate, driveDate) {
    if (!confirm('确定要删除这条驾驶记录吗？')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/drive`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                driver_id: driverId,
                license_plate: licensePlate,
                drive_date: driveDate
            })
        });

        if (response.ok) {
            loadDriveRecords();
        } else {
            const error = await response.json();
            alert(error.message || '删除驾驶记录失败');
        }
    } catch (error) {
        console.error('删除驾驶记录失败:', error);
        alert('删除驾驶记录失败');
    }
}

// 添加车队
async function addFleet(event) {
    event.preventDefault();
    const name = document.getElementById('fleetName').value;

    try {
        const response = await fetch(`${API_BASE_URL}/fleet`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name })
        });

        if (response.ok) {
            document.getElementById('fleetForm').reset();
            loadFleets();
        } else {
            const error = await response.json();
            alert(error.message || '添加车队失败');
        }
    } catch (error) {
        console.error('添加车队失败:', error);
        alert('添加车队失败');
    }
}

// 添加车辆
async function addVehicle(event) {
    event.preventDefault();
    const vehicle = {
        license_plate: document.getElementById('licensePlate').value,
        manufacturer: document.getElementById('manufacturer').value,
        production_date: document.getElementById('productionDate').value,
        fleet_id: document.getElementById('fleetId').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/vehicle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(vehicle)
        });

        if (response.ok) {
            document.getElementById('vehicleForm').reset();
            loadVehicles();
        } else {
            const error = await response.json();
            alert(error.message || '添加车辆失败');
        }
    } catch (error) {
        console.error('添加车辆失败:', error);
        alert('添加车辆失败');
    }
}

// 添加驾驶员
async function addDriver(event) {
    event.preventDefault();
    const driver = {
        name: document.getElementById('driverName').value,
        phone: document.getElementById('driverPhone').value,
        fleet_id: document.getElementById('driverFleetId').value,
        hire_period: document.getElementById('hirePeriod').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/driver`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(driver)
        });

        if (response.ok) {
            document.getElementById('driverForm').reset();
            loadDrivers();
        } else {
            const error = await response.json();
            alert(error.message || '添加驾驶员失败');
        }
    } catch (error) {
        console.error('添加驾驶员失败:', error);
        alert('添加驾驶员失败');
    }
}

// 添加驾驶记录
async function addDriveRecord(event) {
    event.preventDefault();
    const record = {
        driver_id: document.getElementById('driveDriverId').value,
        license_plate: document.getElementById('driveLicensePlate').value,
        drive_date: document.getElementById('driveDate').value,
        mileage: document.getElementById('mileage').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/drive`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(record)
        });

        if (response.ok) {
            document.getElementById('driveForm').reset();
            loadDriveRecords();
        } else {
            const error = await response.json();
            alert(error.message || '添加驾驶记录失败');
        }
    } catch (error) {
        console.error('添加驾驶记录失败:', error);
        alert('添加驾驶记录失败');
    }
}

// 加载驾驶员选项
async function loadDriverOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/driver`);
        const drivers = await response.json();
        const select = document.getElementById('driveDriverId');
        select.innerHTML = '<option value="">选择驾驶员</option>';
        drivers.forEach(driver => {
            const option = document.createElement('option');
            option.value = driver.driver_id;
            option.textContent = `${driver.name} (${driver.phone})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('加载驾驶员选项失败:', error);
        alert('加载驾驶员选项失败');
    }
}

// 加载车辆选项
async function loadVehicleOptions() {
    try {
        const response = await fetch(`${API_BASE_URL}/vehicle`);
        const vehicles = await response.json();
        const select = document.getElementById('driveLicensePlate');
        select.innerHTML = '<option value="">选择车辆</option>';
        vehicles.forEach(vehicle => {
            const option = document.createElement('option');
            option.value = vehicle.license_plate;
            option.textContent = `${vehicle.license_plate} - ${vehicle.manufacturer}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('加载车辆选项失败:', error);
        alert('加载车辆选项失败');
    }
}