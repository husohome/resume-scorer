<template>
  <el-config-provider :locale="zhCn">
    <div class="app">
      <el-container>
        <el-header>
          <el-menu mode="horizontal" :router="true" :default-active="activeMenu">
            <el-menu-item index="/criteria">评估标准管理</el-menu-item>
            <el-menu-item index="/resume">简历评估</el-menu-item>
          </el-menu>
        </el-header>

        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import zhCn from 'element-plus/dist/locale/zh-cn.mjs';

const route = useRoute();
const activeMenu = computed(() => route.path);
</script>

<style lang="scss">
@import './styles/main.scss';

.app {
  min-height: 100vh;
}

.el-header {
  padding: 0;
  border-bottom: 1px solid $border-color;
}

.el-main {
  background-color: $bg-color;
}
</style>
