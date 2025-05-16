import axios from 'axios';

export default class ReportService {
    static downloadReportOfDefect = async (id, report_type='pdf') => {
        try {
            if (report_type === 'pdf') {
                return await axios.post(`http://127.0.0.1:8000/api/v1/report/id=${id}/pdf`);
            } else if (report_type === 'csv') {
                return await axios.post(`http://127.0.0.1:8000/api/v1/report/id=${id}/csv`);
            }
        } catch (error) {
            throw error;
        }
    }

    static downloadReportOfAllDefects = async (report_type='pdf') => {
        try {
            if (report_type === 'pdf') {
                return await axios.post(`http://127.0.0.1:8000/api/v1/report/all/pdf`);
            } else if (report_type === 'csv') {
                return await axios.post(`http://127.0.0.1:8000/api/v1/report/all/csv`);
            }
        } catch (error) {
            throw error;
        }
    }

    static downloadReportOfConveyorStateAndParameters = async (report_type='pdf') => {
        try {
            if (report_type === 'pdf') {
                return await axios.post(`http://127.0.0.1:8000/api/v1/report/conveyor/pdf`);
            } else if (report_type === 'csv') {
                return await axios.post(`http://127.0.0.1:8000/api/v1/report/conveyor/csv`);
            }
        } catch (error) {
            throw error;
        }
    }
}
