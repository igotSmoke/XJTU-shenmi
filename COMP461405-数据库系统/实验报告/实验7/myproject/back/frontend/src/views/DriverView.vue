<template>
  <div class="driver-container">
    <div class="header">
      <h2>司机管理</h2>
      <el-button type="primary" @click="showAddDialog">添加司机</el-button>
    </div>

    <el-table :data="drivers" style="width: 100%">
      <el-table-column prop="driver_id" label="ID" width="80" />
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="phone" label="电话" />
      <el-table-column prop="fleet_id" label="所属车队" width="100" />
      <el-table-column prop="hire_period" label="雇佣期限" />
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
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { driverApi, fleetApi } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const drivers = ref([])
const fleets = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({
  driver_id: null,
  name: '',
  phone: '',
  fleet_id: null,
  hire_period: ''
})

// 加载司机列表
const loadDrivers = async () => {
  try {
    const response = await driverApi.getAll()
    drivers.value = response.data
  } catch (error) {
    ElMessage.error('加载司机列表失败')
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
  dialogTitle.value = '添加司机'
  form.value = {
    driver_id: null,
    name: '',
    phone: '',
    fleet_id: null,
    hire_period: ''
  }
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (row) => {
  dialogTitle.value = '编辑司机'
  form.value = { ...row }
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    if (form.value.driver_id) {
      await driverApi.update(form.value.driver_id, form.value)
      ElMessage.success('更新成功')
    } else {
      await driverApi.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadDrivers()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除司机
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个司机吗？', '提示', {
      type: 'warning'
    })
    await driverApi.delete(row.driver_id)
    ElMessage.success('删除成功')
    loadDrivers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadDrivers()
  loadFleets()
})
</script>

<style scoped>
.driver-container {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style> 