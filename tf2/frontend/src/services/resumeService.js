import api from './api';

export const resumeService = {
  async setFolder(path) {
    return await api.post('/resumes/folder', path);
  },

  async getMetadata() {
    return await api.get('/resumes/metadata');
  },

  async getResume(filename) {
    return await api.get(`/resumes/${filename}`);
  },

  async scoreResume(criteriaName, filename) {
    return await api.post(`/scorers/${criteriaName}/${filename}`);
  },

  async getScoreDetails(criteriaName, filename) {
    return await api.get(`/scorers/results/${criteriaName}/${filename}`);
  }
};
