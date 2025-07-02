<template>
  <el-container>
    <el-aside width="200px">
      <el-menu
        router
        :default-active="$route.path"
        class="el-menu-vertical">
        <el-menu-item index="/fleets">
          <el-icon><Van /></el-icon>
          <span>车队管理</span>
        </el-menu-item>
        <el-menu-item index="/vehicles">
          <el-icon><Car /></el-icon>
          <span>车辆管理</span>
        </el-menu-item>
        <el-menu-item index="/drivers">
          <el-icon><User /></el-icon>
          <span>司机管理</span>
        </el-menu-item>
        <el-menu-item index="/drives">
          <el-icon><List /></el-icon>
          <span>驾驶记录</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<script setup>
import { Van, Car, User, List } from '@element-plus/icons-vue'
</script>

<style>
.el-container {
  height: 100vh;
}
.el-aside {
  background-color: #545c64;
}
.el-menu {
  border-right: none;
}
</style> 