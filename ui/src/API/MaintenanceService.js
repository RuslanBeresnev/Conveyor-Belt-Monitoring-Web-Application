import axios from 'axios';

export default class MaintenanceService {
    static checkServer = async () => {
        try {
            return await axios.get('http://127.0.0.1:8000/api/v1/maintenance/check_server');
        } catch (error) {
            throw error;
        }
    }

    static checkDatabase = async () => {
        try {
            return await axios.get('http://127.0.0.1:8000/api/v1/maintenance/check_database');
        } catch (error) {
            throw error;
        }
    }
}
