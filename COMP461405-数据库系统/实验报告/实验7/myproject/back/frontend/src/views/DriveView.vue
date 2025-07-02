<template>
  <div class="drive-container">
    <div class="header">
      <h2>驾驶记录管理</h2>
      <el-button type="primary" @click="showAddDialog">添加记录</el-button>
    </div>

    <el-table :data="drives" style="width: 100%">
      <el-table-column prop="driver_id" label="司机ID" width="80" />
      <el-table-column prop="license_plate" label="车牌号" width="120" />
      <el-table-column prop="drive_date" label="驾驶日期" width="120" />
      <el-table-column prop="mileage" label="里程数" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="30%">
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
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { driveApi, driverApi, vehicleApi } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const drives = ref([])
const drivers = ref([])
const vehicles = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({
  driver_id: null,
  license_plate: '',
  drive_date: '',
  mileage: 0
})

// 加载驾驶记录列表
const loadDrives = async () => {
  try {
    const response = await driveApi.getAll()
    drives.value = response.data
  } catch (error) {
    ElMessage.error('加载驾驶记录列表失败')
  }
}

// 加载司机列表
const loadDrivers = async () => {
  try {
    const response = await driverApi.getAll()
    drivers.value = response.data
  } catch (error) {
    ElMessage.error('加载司机列表失败')
  }
}

// 加载车辆列表
const loadVehicles = async () => {
  try {
    const response = await vehicleApi.getAll()
    vehicles.value = response.data
  } catch (error) {
    ElMessage.error('加载车辆列表失败')
  }
}

// 显示添加对话框
const showAddDialog = () => {
  dialogTitle.value = '添加驾驶记录'
  form.value = {
    driver_id: null,
    license_plate: '',
    drive_date: '',
    mileage: 0
  }
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (row) => {
  dialogTitle.value = '编辑驾驶记录'
  form.value = { ...row }
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    if (form.value.driver_id && form.value.license_plate && form.value.drive_date) {
      await driveApi.update(
        form.value.driver_id,
        form.value.license_plate,
        form.value.drive_date,
        form.value
      )
      ElMessage.success('更新成功')
    } else {
      await driveApi.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadDrives()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除驾驶记录
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条驾驶记录吗？', '提示', {
      type: 'warning'
    })
    await driveApi.delete(row.driver_id, row.license_plate, row.drive_date)
    ElMessage.success('删除成功')
    loadDrives()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadDrives()
  loadDrivers()
  loadVehicles()
})
</script>

<style scoped>
.drive-container {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style> 