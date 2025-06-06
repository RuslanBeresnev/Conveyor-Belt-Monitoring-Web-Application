import axios from "axios";
import AuthenticationUtils from "../utils/AuthenticationUtils";

export function createServiceApi(serviceName) {
    const serviceApi = axios.create({
        baseURL: `http://${process.env.REACT_APP_SERVER_ADDRESS}:${process.env.REACT_APP_CONNECTION_PORT}/api/v1/${serviceName}`,
        headers: {
            "Content-Type": "application/json",
        },
    });

    if (serviceName === 'auth') return serviceApi;

    serviceApi.interceptors.request.use(
        (config) => {
            const token = localStorage.getItem('access_token');
            if (token) {
                config.headers["Authorization"] = `Bearer ${token}`;
            }
            return config;
        }
    );

    serviceApi.interceptors.response.use(
        response => response,
        error => {
            if (error.response?.status === 401) {
                AuthenticationUtils.logout();
            }
            return Promise.reject(error);
        }
    );

    return serviceApi;
}
