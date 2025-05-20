import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/v1/report',
});

export default class ReportService {
    static downloadReportOfDefect = async (id, report_type='pdf') => {
        if (report_type === 'pdf') {
            return await api.post(`/id=${id}/pdf`);
        } else if (report_type === 'csv') {
            return await api.post(`/id=${id}/csv`);
        }
    }

    static downloadReportOfAllDefects = async (report_type='pdf') => {
        if (report_type === 'pdf') {
            return await api.post('/all/pdf');
        } else if (report_type === 'csv') {
            return await api.post('/all/csv');
        }
    }

    static downloadReportOfConveyorStateAndParameters = async (report_type='pdf') => {
        if (report_type === 'pdf') {
            return await api.post('/conveyor/pdf');
        } else if (report_type === 'csv') {
            return await api.post('/conveyor/csv');
        }
    }
}
