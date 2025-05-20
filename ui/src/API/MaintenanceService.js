import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/v1/maintenance',
});

export default class MaintenanceService {
    static checkServer = async () => await api.get('/check_server')

    static checkDatabase = async () => await api.get('/check_database')
}
