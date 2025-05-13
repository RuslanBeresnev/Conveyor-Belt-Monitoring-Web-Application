import axios from 'axios';
import dayjs from "dayjs";

export default class DefectInfoService {
    static getAllDefects = async () => {
        try {
            return await axios.get('http://127.0.0.1:8000/api/v1/defect_info/all');
        } catch (error) {
            throw error;
        }
    }

    static getFilteredDefects = async (defect_type='all', criticality='all', start_datetime, end_datetime) => {
        try {
            if (!start_datetime) {
                start_datetime = dayjs(0);
            }
            if (!end_datetime) {
                end_datetime = dayjs();
            }
            return await axios.get(`http://127.0.0.1:8000/api/v1/defect_info/filtered?defect_type=${defect_type}&criticality=${criticality}&start_datetime=${start_datetime.toISOString()}&end_datetime=${end_datetime.toISOString()}`);
        } catch (error) {
            throw error;
        }
    }

    static getAllTypesOfDefects = async () => {
        try {
            return await axios.get('http://127.0.0.1:8000/api/v1/defect_info/all_types');
        } catch (error) {
            throw error;
        }
    }
}
