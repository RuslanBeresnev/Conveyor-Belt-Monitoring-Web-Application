import {createServiceApi} from "./BaseAPI";

const api = createServiceApi('maintenance')

export default class MaintenanceService {
    static checkServer = async () => await api.get('/check_server')

    static checkDatabase = async () => await api.get('/check_database')
}
