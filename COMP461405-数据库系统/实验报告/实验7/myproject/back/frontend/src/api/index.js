import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

// 车队相关API
export const fleetApi = {
  getAll: () => api.get('/fleets/'),
  create: (data) => api.post('/fleets/', data),
  update: (id, data) => api.put(`/fleets/${id}`, data),
  delete: (id) => api.delete(`/fleets/${id}`)
}

// 车辆相关API
export const vehicleApi = {
  getAll: () => api.get('/vehicles/'),
  create: (data) => api.post('/vehicles/', data),
  update: (id, data) => api.put(`/vehicles/${id}`, data),
  delete: (id) => api.delete(`/vehicles/${id}`)
}

// 司机相关API
export const driverApi = {
  getAll: () => api.get('/drivers/'),
  create: (data) => api.post('/drivers/', data),
  update: (id, data) => api.put(`/drivers/${id}`, data),
  delete: (id) => api.delete(`/drivers/${id}`)
}

// 驾驶记录相关API
export const driveApi = {
  getAll: () => api.get('/drives/'),
  create: (data) => api.post('/drives/', data),
  update: (driverId, licensePlate, driveDate, data) => 
    api.put(`/drives/${driverId}/${licensePlate}/${driveDate}`, data),
  delete: (driverId, licensePlate, driveDate) => 
    api.delete(`/drives/${driverId}/${licensePlate}/${driveDate}`)
} 