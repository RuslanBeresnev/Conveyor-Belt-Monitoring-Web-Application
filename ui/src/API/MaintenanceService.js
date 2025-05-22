import {createServiceApi} from "./BaseAPI";

const api = createServiceApi('maintenance')

export default class MaintenanceService {
    static checkServer = async () => await api.get('/check_server')

    static checkDatabase = async () => await api.get('/check_database')

    static getUserNotificationSettings = async () => await api.get('/get_user_notification_settings')

    static updateUserNotificationSettings = async (on_new_defect_notification_scope=["Telegram", "Gmail"],
                                                report_sending_scope=["Telegram", "Gmail"]) =>
        await api.put('/update_user_notification_settings', {
            "new_defect_notification_scope": on_new_defect_notification_scope,
            "report_sending_scope": report_sending_scope
        })
}
