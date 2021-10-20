import axios from 'axios';
import {toast} from 'react-toastify';
import {BASE_URL} from './constants';

const API = axios.create(
  { baseURL: `${BASE_URL}/api` },
  {
    headers: {
      'Content-Type': 'multipart/form-data'
  }}
);

// API.interceptors.request.use((req) => {
//   if (localStorage.getItem('profile')) {
//     req.headers.Authorization = `Bearer ${JSON.parse(localStorage.getItem('profile')).token}`;
//   } else {
//     window.location.href = "/";
//   }
//   return req;
// });




export const signIn = (formData) => API.post('/token/', formData);
