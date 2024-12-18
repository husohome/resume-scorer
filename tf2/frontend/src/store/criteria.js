import { defineStore } from 'pinia';
import { criteriaService } from '../../services/criteriaService';

export const useCriteriaStore = defineStore('criteria', {
  state: () => ({
    criteriaList: [],
    selectedCriteria: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchCriteriaList() {
      this.loading = true;
      try {
        this.criteriaList = await criteriaService.listAll();
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    async selectCriteria(name) {
      try {
        this.selectedCriteria = await criteriaService.getCriteria(name);
      } catch (error) {
        this.error = error.message;
      }
    }
  }
});
