import {createServiceApi} from "./BaseAPI";

const api = createServiceApi('notification')

export default class NotificationService {
    static sendTelegramNotification = async (message) =>
        await api.post('/with_telegram', null,{ params: { message: message } })

    static sendGmailNotification = async (subject, text) =>
        await api.post('/with_gmail', null, { params: { subject: subject, text: text } })
}
