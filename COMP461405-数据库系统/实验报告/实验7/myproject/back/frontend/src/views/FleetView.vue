<template>
  <div class="fleet-container">
    <div class="header">
      <h2>车队管理</h2>
      <el-button type="primary" @click="showAddDialog">添加车队</el-button>
    </div>

    <el-table :data="fleets" style="width: 100%">
      <el-table-column prop="fleet_id" label="ID" width="80" />
      <el-table-column prop="name" label="车队名称" />
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
      <el-form :model="form" label-width="80px">
        <el-form-item label="车队名称">
          <el-input v-model="form.name" />
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
import { fleetApi } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const fleets = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({
  fleet_id: null,
  name: ''
})

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
  dialogTitle.value = '添加车队'
  form.value = { fleet_id: null, name: '' }
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (row) => {
  dialogTitle.value = '编辑车队'
  form.value = { ...row }
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    if (form.value.fleet_id) {
      await fleetApi.update(form.value.fleet_id, form.value)
      ElMessage.success('更新成功')
    } else {
      await fleetApi.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadFleets()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除车队
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个车队吗？', '提示', {
      type: 'warning'
    })
    await fleetApi.delete(row.fleet_id)
    ElMessage.success('删除成功')
    loadFleets()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadFleets()
})
</script>

<style scoped>
.fleet-container {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style> 