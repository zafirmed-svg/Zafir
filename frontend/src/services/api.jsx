import axios from 'axios';

// En desarrollo usamos el proxy de Vite, en producción la URL completa
const baseURL = process.env.NODE_ENV === 'production' 
    ? import.meta.env.VITE_API_URL 
    : '/api';

const api = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: false,
    validateStatus: status => status < 500, // Acepta todos los códigos de estado por debajo de 500
    timeout: 10000 // 10 segundos de timeout
});

//servicios para cotizaciones
export const quoteService = {
    getAll: () => api.get('/quotes/'),
    getById: (id) => api.get(`/quotes/${id}/`),
    create: (data) => api.post('/quotes/', data),
    update: (id, data) => api.put(`/quotes/${id}/`, data),
    delete: (id) => api.delete(`/quotes/${id}/`),
    updateStatus: (id, status) => api.post(`/quotes/${id}/update_status/`, { status })
}

//servicios para paquetes quirurgicos
export const packageService = {
    getAll: () => api.get('/packages/'),
    getById: (id) => api.get(`/packages/${id}/`),
    create: (data) => api.post('/packages/', data),
    update: (id, data) => api.put(`/packages/${id}/`, data),
    delete: (id) => api.delete(`/packages/${id}/`)
}

//manejador de errores global
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response) {
            // La respuesta fue hecha y el servidor respondió con un código de estado
            // que cae fuera del rango 2xx
            console.error('API Error Response:', {
                status: error.response.status,
                data: error.response.data,
                headers: error.response.headers,
            });
        } else if (error.request) {
            // La petición fue hecha pero no se recibió respuesta
            console.error('API Error Request:', error.request);
        } else {
            // Algo sucedió en la configuración de la petición que provocó un error
            console.error('API Error Setup:', error.message);
        }
        console.error('API Error Config:', error.config);
        return Promise.reject(error);
    }
);

export default api;