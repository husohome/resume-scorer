import { defineStore } from 'pinia';
import { resumeService } from '../services/resumeService';

export const useResumeStore = defineStore('resume', {
  state: () => ({
    resumeList: [],
    currentResume: null,
    scoreResult: null,
    loading: false,
    error: null
  }),

  actions: {
    async setFolder(path) {
      this.loading = true;
      try {
        await resumeService.setFolder(path);
        const metadata = await resumeService.getMetadata();
        this.resumeList = metadata;
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    async viewResume(filename) {
      this.loading = true;
      try {
        const resume = await resumeService.getResume(filename);
        this.currentResume = resume;
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    async scoreResume(criteriaName, filename) {
      this.loading = true;
      try {
        const result = await resumeService.getScoreDetails(criteriaName, filename);
        this.scoreResult = result;
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    }
  }
});
