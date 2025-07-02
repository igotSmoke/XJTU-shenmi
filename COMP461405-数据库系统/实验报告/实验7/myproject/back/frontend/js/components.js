// 车队对话框组件
const FleetDialog = {
    props: ['visible', 'fleet'],
    template: `
        <el-dialog
            :title="fleet.fleet_id ? '编辑车队' : '添加车队'"
            v-model="dialogVisible"
            width="30%"
            @close="$emit('close')">
            <el-form :model="form" label-width="80px">
                <el-form-item label="车队名称">
                    <el-input v-model="form.name" />
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="$emit('close')">取消</el-button>
                    <el-button type="primary" @click="handleSubmit">确定</el-button>
                </span>
            </template>
        </el-dialog>
    `,
    data() {
        return {
            dialogVisible: this.visible,
            form: {
                fleet_id: null,
                name: ''
            }
        }
    },
    watch: {
        visible(val) {
            this.dialogVisible = val
        },
        fleet: {
            handler(val) {
                this.form = { ...val }
            },
            deep: true
        }
    },
    methods: {
        handleSubmit() {
            this.$emit('submit', this.form)
        }
    }
}

// 车辆对话框组件
const VehicleDialog = {
    props: ['visible', 'vehicle', 'fleets'],
    template: `
        <el-dialog
            :title="vehicle.license_plate ? '编辑车辆' : '添加车辆'"
            v-model="dialogVisible"
            width="30%"
            @close="$emit('close')">
            <el-form :model="form" label-width="100px">
                <el-form-item label="车牌号">
                    <el-input v-model="form.license_plate" :disabled="!!vehicle.license_plate" />
                </el-form-item>
                <el-form-item label="制造商">
                    <el-input v-model="form.manufacturer" />
                </el-form-item>
                <el-form-item label="生产日期">
                    <el-date-picker
                        v-model="form.production_date"
                        type="date"
                        placeholder="选择日期"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                    />
                </el-form-item>
                <el-form-item label="所属车队">
                    <el-select v-model="form.fleet_id" placeholder="选择车队">
                        <el-option
                            v-for="fleet in fleets"
                            :key="fleet.fleet_id"
                            :label="fleet.name"
                            :value="fleet.fleet_id"
                        />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="$emit('close')">取消</el-button>
                    <el-button type="primary" @click="handleSubmit">确定</el-button>
                </span>
            </template>
        </el-dialog>
    `,
    data() {
        return {
            dialogVisible: this.visible,
            form: {
                license_plate: '',
                manufacturer: '',
                production_date: '',
                fleet_id: null
            }
        }
    },
    watch: {
        visible(val) {
            this.dialogVisible = val
        },
        vehicle: {
            handler(val) {
                this.form = { ...val }
            },
            deep: true
        }
    },
    methods: {
        handleSubmit() {
            this.$emit('submit', this.form)
        }
    }
}

// 司机对话框组件
const DriverDialog = {
    props: ['visible', 'driver', 'fleets'],
    template: `
        <el-dialog
            :title="driver.driver_id ? '编辑司机' : '添加司机'"
            v-model="dialogVisible"
            width="30%"
            @close="$emit('close')">
            <el-form :model="form" label-width="100px">
                <el-form-item label="姓名">
                    <el-input v-model="form.name" />
                </el-form-item>
                <el-form-item label="电话">
                    <el-input v-model="form.phone" />
                </el-form-item>
                <el-form-item label="所属车队">
                    <el-select v-model="form.fleet_id" placeholder="选择车队">
                        <el-option
                            v-for="fleet in fleets"
                            :key="fleet.fleet_id"
                            :label="fleet.name"
                            :value="fleet.fleet_id"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="雇佣期限">
                    <el-input v-model="form.hire_period" />
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="$emit('close')">取消</el-button>
                    <el-button type="primary" @click="handleSubmit">确定</el-button>
                </span>
            </template>
        </el-dialog>
    `,
    data() {
        return {
            dialogVisible: this.visible,
            form: {
                driver_id: null,
                name: '',
                phone: '',
                fleet_id: null,
                hire_period: ''
            }
        }
    },
    watch: {
        visible(val) {
            this.dialogVisible = val
        },
        driver: {
            handler(val) {
                this.form = { ...val }
            },
            deep: true
        }
    },
    methods: {
        handleSubmit() {
            this.$emit('submit', this.form)
        }
    }
}

// 驾驶记录对话框组件
const DriveDialog = {
    props: ['visible', 'drive', 'drivers', 'vehicles'],
    template: `
        <el-dialog
            :title="drive.driver_id ? '编辑驾驶记录' : '添加驾驶记录'"
            v-model="dialogVisible"
            width="30%"
            @close="$emit('close')">
            <el-form :model="form" label-width="100px">
                <el-form-item label="司机">
                    <el-select v-model="form.driver_id" placeholder="选择司机">
                        <el-option
                            v-for="driver in drivers"
                            :key="driver.driver_id"
                            :label="driver.name"
                            :value="driver.driver_id"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="车辆">
                    <el-select v-model="form.license_plate" placeholder="选择车辆">
                        <el-option
                            v-for="vehicle in vehicles"
                            :key="vehicle.license_plate"
                            :label="vehicle.license_plate"
                            :value="vehicle.license_plate"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="驾驶日期">
                    <el-date-picker
                        v-model="form.drive_date"
                        type="date"
                        placeholder="选择日期"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                    />
                </el-form-item>
                <el-form-item label="里程数">
                    <el-input-number v-model="form.mileage" :min="0" />
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="$emit('close')">取消</el-button>
                    <el-button type="primary" @click="handleSubmit">确定</el-button>
                </span>
            </template>
        </el-dialog>
    `,
    data() {
        return {
            dialogVisible: this.visible,
            form: {
                driver_id: null,
                license_plate: '',
                drive_date: '',
                mileage: 0
            }
        }
    },
    watch: {
        visible(val) {
            this.dialogVisible = val
        },
        drive: {
            handler(val) {
                this.form = { ...val }
            },
            deep: true
        }
    },
    methods: {
        handleSubmit() {
            this.$emit('submit', this.form)
        }
    }
}

// 注册组件
app.component('fleet-dialog', FleetDialog)
app.component('vehicle-dialog', VehicleDialog)
app.component('driver-dialog', DriverDialog)
app.component('drive-dialog', DriveDialog) 