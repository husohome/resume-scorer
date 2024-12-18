<template>
  <div class="criteria-tree">
    <el-tree
      :data="treeData"
      node-key="name"
      default-expand-all
      :props="defaultProps"
    >
      <template #default="{ node, data }">
        <div class="node-content">
          <span>{{ data.name }}</span>
          <span v-if="data.weight" class="weight">权重: {{ data.weight }}</span>
          <el-tooltip v-if="data.content" effect="dark" :content="data.content" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { InfoFilled } from '@element-plus/icons-vue';

const props = defineProps({
  criteria: {
    type: Object,
    required: true
  }
});

const defaultProps = {
  children: 'children',
  label: 'name'
};

const treeData = computed(() => {
  const transformNode = (node) => ({
    name: node.name,
    content: node.content,
    weight: node.weight,
    children: node.children.map(([weight, child]) => ({
      ...transformNode(child),
      weight
    }))
  });
  return [transformNode(props.criteria)];
});
</script>

<style lang="scss" scoped>
.criteria-tree {
  padding: 10px;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.weight {
  color: #666;
  font-size: 0.9em;
}
</style>
