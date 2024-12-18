import axios from 'axios';

const api = axios.create({
  baseURL: '/api',  // 这将直接使用相对路径，由 FastAPI 提供服务
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;