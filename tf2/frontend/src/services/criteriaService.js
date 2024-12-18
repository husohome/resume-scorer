import api from './api';

export const criteriaService = {
  async listAll() {
    return await api.get('/criteria/list/json');
  },

  async getCriteria(name) {
    return await api.get(`/criteria/json/${name}`);
  },

  async createCriteria(data) {
    return await api.post('/criteria/json', data);
  },

  async updateCriteria(name, data) {
    return await api.put(`/criteria/json/${name}`, data);
  },

  async deleteCriteria(name) {
    return await api.delete(`/criteria/${name}`);
  }
};
