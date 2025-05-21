import {createServiceApi} from "./BaseAPI";

const api = createServiceApi('logs')

export default class LoggingService {
    static getAllLogs = async () =>
        await api.get('/all');

    static deleteLogById = async (id, needToLog) =>
        await api.delete(`/id=${id}/delete?log_deletion_event=${needToLog}`);

    static deleteAllLogs = async (needToLog) =>
        await api.delete(`/delete_all?log_deletion_event=${needToLog}`);
}
