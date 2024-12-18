<template>
  <div class="resume-scoring">
    <el-row :gutter="20">
      <!-- 左侧：文件夹设置和简历列表 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>简历管理</span>
            </div>
          </template>
          
          <!-- 文件夹路径设置 -->
          <el-input
            v-model="resumePath"
            placeholder="设置简历文件夹路径"
            clearable
          >
            <template #append>
              <el-button @click="setFolder">设置</el-button>
            </template>
          </el-input>

          <!-- 简历列表 -->
          <el-table :data="resumeList" style="margin-top: 20px;">
            <el-table-column prop="filename" label="文件名" />
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button @click="viewResume(row)">查看</el-button>
                <el-button type="primary" @click="scoreResume(row)">评分</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：简历内容和评分结果 -->
      <el-col :span="16">
        <el-card v-if="currentResume">
          <template #header>
            <div class="card-header">
              <span>简历内容 - {{ currentResume.filename }}</span>
              <el-select v-model="selectedCriteria" placeholder="选择评估标准">
                <el-option
                  v-for="item in criteriaList"
                  :key="item.name"
                  :label="item.name"
                  :value="item.name"
                />
              </el-select>
            </div>
          </template>
          
          <div class="resume-content">
            <div v-for="(page, index) in currentResume.content" :key="index">
              <h3>第 {{ index + 1 }} 页</h3>
              <p>{{ page }}</p>
            </div>
          </div>
        </el-card>

        <!-- 评分结果 -->
        <score-display
          v-if="scoreResult"
          :score-result="scoreResult"
          class="mt-4"
        />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useResumeStore } from '../store/resume';
import { useCriteriaStore } from '../store/criteria';
import ScoreDisplay from './ScoreDisplay.vue';

const resumeStore = useResumeStore();
const criteriaStore = useCriteriaStore();

const resumePath = ref('');
const selectedCriteria = ref('');
const { resumeList, currentResume, scoreResult } = storeToRefs(resumeStore);
const { criteriaList } = storeToRefs(criteriaStore);

onMounted(async () => {
  await criteriaStore.fetchCriteriaList();
});

const setFolder = async () => {
  await resumeStore.setFolder(resumePath.value);
};

const viewResume = async (resume) => {
  await resumeStore.viewResume(resume.filename);
};

const scoreResume = async (resume) => {
  if (!selectedCriteria.value) {
    ElMessage.warning('请先选择评估标准');
    return;
  }
  await resumeStore.scoreResume(selectedCriteria.value, resume.filename);
};
</script>

<style lang="scss" scoped>
.resume-scoring {
  padding: 20px;
}

.resume-content {
  max-height: 500px;
  overflow-y: auto;
  padding: 10px;
}

.mt-4 {
  margin-top: 1rem;
}
</style>
