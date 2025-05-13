import axios from 'axios';

export default class DefectInfoService {
    static getAllDefects = async () => {
        try {
            return await axios.get('http://127.0.0.1:8000/api/v1/defect_info/all');
        } catch (error) {
            throw error;
        }
    }

    static getFilteredDefects = async (defect_type='all') => {
        try {
            return await axios.get(`http://127.0.0.1:8000/api/v1/defect_info/filtered?defect_type=${defect_type}`);
        } catch (error) {
            throw error;
        }
    }
}
