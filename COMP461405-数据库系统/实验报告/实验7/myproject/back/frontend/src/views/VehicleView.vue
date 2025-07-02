<template>
  <div class="vehicle-container">
    <div class="header">
      <h2>车辆管理</h2>
      <el-button type="primary" @click="showAddDialog">添加车辆</el-button>
    </div>

    <el-table :data="vehicles" style="width: 100%">
      <el-table-column prop="license_plate" label="车牌号" width="120" />
      <el-table-column prop="manufacturer" label="制造商" />
      <el-table-column prop="production_date" label="生产日期" width="120" />
      <el-table-column prop="fleet_id" label="所属车队" width="100" />
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
        <el-form-item label="车牌号">
          <el-input v-model="form.license_plate" :disabled="!!form.license_plate" />
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
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { vehicleApi, fleetApi } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const vehicles = ref([])
const fleets = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({
  license_plate: '',
  manufacturer: '',
  production_date: '',
  fleet_id: null
})

// 加载车辆列表
const loadVehicles = async () => {
  try {
    const response = await vehicleApi.getAll()
    vehicles.value = response.data
  } catch (error) {
    ElMessage.error('加载车辆列表失败')
  }
}

// 加载车队列表
const loadFleets = async () => {
  try {
    const response = await fleetApi.getAll()
    fleets.value = response.data
  } catch (error) {
    ElMessage.error('加载车队列表失败')
  }
}

// 显示添加对话框
const showAddDialog = () => {
  dialogTitle.value = '添加车辆'
  form.value = {
    license_plate: '',
    manufacturer: '',
    production_date: '',
    fleet_id: null
  }
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (row) => {
  dialogTitle.value = '编辑车辆'
  form.value = { ...row }
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    if (form.value.license_plate) {
      await vehicleApi.update(form.value.license_plate, form.value)
      ElMessage.success('更新成功')
    } else {
      await vehicleApi.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadVehicles()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除车辆
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这辆车吗？', '提示', {
      type: 'warning'
    })
    await vehicleApi.delete(row.license_plate)
    ElMessage.success('删除成功')
    loadVehicles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadVehicles()
  loadFleets()
})
</script>

<style scoped>
.vehicle-container {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style> 