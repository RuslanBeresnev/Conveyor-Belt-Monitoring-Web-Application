import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/v1/logs',
});

export default class LoggingService {
    static getAllLogs = async () =>
        await api.get('/all');

    static deleteLogById = async (id, logDeletionEvent) =>
        await api.delete(`/id=${id}/delete?log_deletion_event=${logDeletionEvent}`);
}
