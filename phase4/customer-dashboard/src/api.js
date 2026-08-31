import axios from "axios";


export const BASE_URL =
    import.meta.env.VITE_API_URL || "http://localhost:8000";


const api = axios.create({
    baseURL: BASE_URL,

    headers: {
        "X-API-Key": import.meta.env.VITE_API_KEY
    }
});


export default api;