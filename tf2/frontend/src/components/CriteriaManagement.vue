<template>
  <div class="criteria-management">
    <el-row :gutter="20">
      <el-col :span="8">
        <criteria-list
          :criteria="criteriaList"
          @select="handleSelect"
          @delete="handleDelete"
        />
      </el-col>
      <el-col :span="16">
        <criteria-editor
          v-if="selectedCriteria"
          :criteria="selectedCriteria"
          @save="handleSave"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useCriteriaStore } from '../store/criteria';
import CriteriaList from './CriteriaList.vue';
import CriteriaEditor from './CriteriaEditor.vue';

const store = useCriteriaStore();
const { criteriaList, selectedCriteria } = storeToRefs(store);

onMounted(() => {
  store.fetchCriteriaList();
});
</script>

<style lang="scss" scoped>
.criteria-management {
  padding: 20px;
}
</style>
