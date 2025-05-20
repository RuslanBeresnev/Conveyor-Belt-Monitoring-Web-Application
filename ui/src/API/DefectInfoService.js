import axios from 'axios';
import dayjs from "dayjs";

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/v1/defect_info',
});

export default class DefectInfoService {
    static getCountOfDefectCriticalityGroups = async () => await api.get('/count')

    static getAllDefects = async () => await api.get('/all')

    static getFilteredDefects = async (defect_type='all', criticality='all', start_datetime, end_datetime) => {
        if (!start_datetime) {
            start_datetime = dayjs(0);
        }
        if (!end_datetime) {
            end_datetime = dayjs();
        }
        return await api.get(`/filtered?defect_type=${defect_type}&criticality=${criticality}&start_datetime=${start_datetime.toISOString()}&end_datetime=${end_datetime.toISOString()}`);
    }

    static getAllTypesOfDefects = async () => await api.get('/all_types')

    static getChainOfPreviousDefectVariationsByDefectId = async (id) => await api.get(`/id=${id}/chain_of_previous`)

    static setNewCriticalityOfDefect = async (id, is_extreme, is_critical) =>
        await api.put(`/id=${id}/set_criticality`, null, {params: {is_extreme: is_extreme, is_critical: is_critical}})

    static deleteDefect = async (id) => await api.delete(`/id=${id}/delete`)
}
