import qs from "qs";
import {createServiceApi} from "./BaseAPI";

const api = createServiceApi('auth')

export default class AuthenticationService {
    static loginAndGetToken = async (username, password) => await api.post('/token',
        qs.stringify({
            username: username,
            password: password
        }),
        {
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        }
    );
}
