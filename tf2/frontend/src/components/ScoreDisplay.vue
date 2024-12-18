<template>
  <el-card class="score-display">
    <template #header>
      <div class="card-header">
        <span>评分结果</span>
      </div>
    </template>

    <div class="score-content">
      <h2 class="total-score">总分：{{ scoreResult.overall_score.toFixed(2) }}</h2>
      
      <el-tree
        :data="[scoreResult.detailed_scores]"
        node-key="name"
        default-expand-all
      >
        <template #default="{ node, data }">
          <div class="score-node">
            <span class="name">{{ data.name }}</span>
            <span class="score">{{ data.score?.toFixed(2) || 'N/A' }}</span>
            <el-progress
              :percentage="(data.score || 0) * 100"
              :format="percentFormat"
              :status="getScoreStatus(data.score)"
            />
          </div>
        </template>
      </el-tree>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  scoreResult: {
    type: Object,
    required: true
  }
});

const percentFormat = (percent) => `${percent.toFixed(1)}%`;

const getScoreStatus = (score) => {
  if (!score) return '';
  if (score >= 0.8) return 'success';
  if (score >= 0.6) return 'warning';
  return 'exception';
};
</script>

<style lang="scss" scoped>
.score-display {
  .total-score {
    text-align: center;
    margin-bottom: 20px;
    color: #409EFF;
  }

  .score-node {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 5px 0;

    .name {
      min-width: 120px;
    }

    .score {
      min-width: 60px;
      text-align: right;
    }

    .el-progress {
      flex: 1;
    }
  }
}
</style>
