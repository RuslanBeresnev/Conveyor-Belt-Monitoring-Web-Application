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

    static getChainOfPreviousDefectVariationsByDefectId = async (id) => {
        try {
            return await axios.get(`http://127.0.0.1:8000/api/v1/defect_info/id=${id}/chain_of_previous`);
        } catch (error) {
            throw error;
        }
    }

    static setNewCriticalityOfDefect = async (id, is_extreme, is_critical) => {
        try {
            return await axios.put(`http://127.0.0.1:8000/api/v1/defect_info/id=${id}/set_criticality`, null,
                {params: {is_extreme: is_extreme, is_critical: is_critical} });
        } catch (error) {
            throw error;
        }
    }

    static deleteDefect = async (id) => {
        try {
            return await axios.delete(`http://127.0.0.1:8000/api/v1/defect_info/id=${id}/delete`);
        } catch (error) {
            throw error;
        }
    }
}
