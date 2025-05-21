import {createServiceApi} from "./BaseAPI";

const api = createServiceApi('report')

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
