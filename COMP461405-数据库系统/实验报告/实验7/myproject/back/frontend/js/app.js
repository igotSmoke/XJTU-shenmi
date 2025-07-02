// 创建Vue应用
const app = Vue.createApp({
    data() {
        return {
            activeIndex: 'fleets',
            // 车队相关
            fleets: [],
            showFleetDialogVisible: false,
            currentFleet: {},
            // 车辆相关
            vehicles: [],
            showVehicleDialogVisible: false,
            currentVehicle: {},
            // 司机相关
            drivers: [],
            showDriverDialogVisible: false,
            currentDriver: {},
            // 驾驶记录相关
            drives: [],
            showDriveDialogVisible: false,
            currentDrive: {}
        }
    },
    methods: {
        // 菜单选择
        handleSelect(key) {
            this.activeIndex = key
        },

        // 车队相关方法
        async loadFleets() {
            try {
                const response = await axios.get('http://localhost:5000/fleets/')
                this.fleets = response.data
            } catch (error) {
                ElementPlus.ElMessage.error('加载车队列表失败')
            }
        },
        showFleetDialog() {
            this.currentFleet = {}
            this.showFleetDialogVisible = true
        },
        editFleet(row) {
            this.currentFleet = { ...row }
            this.showFleetDialogVisible = true
        },
        async deleteFleet(row) {
            try {
                await ElementPlus.ElMessageBox.confirm('确定要删除这个车队吗？', '提示', {
                    type: 'warning'
                })
                await axios.delete(`http://localhost:5000/fleets/${row.fleet_id}`)
                ElementPlus.ElMessage.success('删除成功')
                this.loadFleets()
            } catch (error) {
                if (error !== 'cancel') {
                    ElementPlus.ElMessage.error('删除失败')
                }
            }
        },
        closeFleetDialog() {
            this.showFleetDialogVisible = false
        },
        async submitFleet(form) {
            try {
                if (form.fleet_id) {
                    await axios.put(`http://localhost:5000/fleets/${form.fleet_id}`, form)
                    ElementPlus.ElMessage.success('更新成功')
                } else {
                    await axios.post('http://localhost:5000/fleets/', form)
                    ElementPlus.ElMessage.success('添加成功')
                }
                this.showFleetDialogVisible = false
                this.loadFleets()
            } catch (error) {
                ElementPlus.ElMessage.error('操作失败')
            }
        },

        // 车辆相关方法
        async loadVehicles() {
            try {
                const response = await axios.get('http://localhost:5000/vehicles/')
                this.vehicles = response.data
            } catch (error) {
                ElementPlus.ElMessage.error('加载车辆列表失败')
            }
        },
        showVehicleDialog() {
            this.currentVehicle = {}
            this.showVehicleDialogVisible = true
        },
        editVehicle(row) {
            this.currentVehicle = { ...row }
            this.showVehicleDialogVisible = true
        },
        async deleteVehicle(row) {
            try {
                await ElementPlus.ElMessageBox.confirm('确定要删除这辆车吗？', '提示', {
                    type: 'warning'
                })
                await axios.delete(`http://localhost:5000/vehicles/${row.license_plate}`)
                ElementPlus.ElMessage.success('删除成功')
                this.loadVehicles()
            } catch (error) {
                if (error !== 'cancel') {
                    ElementPlus.ElMessage.error('删除失败')
                }
            }
        },
        closeVehicleDialog() {
            this.showVehicleDialogVisible = false
        },
        async submitVehicle(form) {
            try {
                if (form.license_plate) {
                    await axios.put(`http://localhost:5000/vehicles/${form.license_plate}`, form)
                    ElementPlus.ElMessage.success('更新成功')
                } else {
                    await axios.post('http://localhost:5000/vehicles/', form)
                    ElementPlus.ElMessage.success('添加成功')
                }
                this.showVehicleDialogVisible = false
                this.loadVehicles()
            } catch (error) {
                ElementPlus.ElMessage.error('操作失败')
            }
        },

        // 司机相关方法
        async loadDrivers() {
            try {
                const response = await axios.get('http://localhost:5000/drivers/')
                this.drivers = response.data
            } catch (error) {
                ElementPlus.ElMessage.error('加载司机列表失败')
            }
        },
        showDriverDialog() {
            this.currentDriver = {}
            this.showDriverDialogVisible = true
        },
        editDriver(row) {
            this.currentDriver = { ...row }
            this.showDriverDialogVisible = true
        },
        async deleteDriver(row) {
            try {
                await ElementPlus.ElMessageBox.confirm('确定要删除这个司机吗？', '提示', {
                    type: 'warning'
                })
                await axios.delete(`http://localhost:5000/drivers/${row.driver_id}`)
                ElementPlus.ElMessage.success('删除成功')
                this.loadDrivers()
            } catch (error) {
                if (error !== 'cancel') {
                    ElementPlus.ElMessage.error('删除失败')
                }
            }
        },
        closeDriverDialog() {
            this.showDriverDialogVisible = false
        },
        async submitDriver(form) {
            try {
                if (form.driver_id) {
                    await axios.put(`http://localhost:5000/drivers/${form.driver_id}`, form)
                    ElementPlus.ElMessage.success('更新成功')
                } else {
                    await axios.post('http://localhost:5000/drivers/', form)
                    ElementPlus.ElMessage.success('添加成功')
                }
                this.showDriverDialogVisible = false
                this.loadDrivers()
            } catch (error) {
                ElementPlus.ElMessage.error('操作失败')
            }
        },

        // 驾驶记录相关方法
        async loadDrives() {
            try {
                const response = await axios.get('http://localhost:5000/drives/')
                this.drives = response.data
            } catch (error) {
                ElementPlus.ElMessage.error('加载驾驶记录列表失败')
            }
        },
        showDriveDialog() {
            this.currentDrive = {}
            this.showDriveDialogVisible = true
        },
        editDrive(row) {
            this.currentDrive = { ...row }
            this.showDriveDialogVisible = true
        },
        async deleteDrive(row) {
            try {
                await ElementPlus.ElMessageBox.confirm('确定要删除这条驾驶记录吗？', '提示', {
                    type: 'warning'
                })
                await axios.delete(`http://localhost:5000/drives/${row.driver_id}/${row.license_plate}/${row.drive_date}`)
                ElementPlus.ElMessage.success('删除成功')
                this.loadDrives()
            } catch (error) {
                if (error !== 'cancel') {
                    ElementPlus.ElMessage.error('删除失败')
                }
            }
        },
        closeDriveDialog() {
            this.showDriveDialogVisible = false
        },
        async submitDrive(form) {
            try {
                if (form.driver_id && form.license_plate && form.drive_date) {
                    await axios.put(
                        `http://localhost:5000/drives/${form.driver_id}/${form.license_plate}/${form.drive_date}`,
                        form
                    )
                    ElementPlus.ElMessage.success('更新成功')
                } else {
                    await axios.post('http://localhost:5000/drives/', form)
                    ElementPlus.ElMessage.success('添加成功')
                }
                this.showDriveDialogVisible = false
                this.loadDrives()
            } catch (error) {
                ElementPlus.ElMessage.error('操作失败')
            }
        }
    },
    mounted() {
        // 加载所有数据
        this.loadFleets()
        this.loadVehicles()
        this.loadDrivers()
        this.loadDrives()
    }
})

// 使用Element Plus
app.use(ElementPlus)

// 挂载应用
app.mount('#app') 