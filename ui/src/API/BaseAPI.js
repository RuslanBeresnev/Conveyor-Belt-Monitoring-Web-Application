import axios from "axios";

export function createServiceApi(serviceName) {
    return axios.create({
        baseURL: `http://${process.env.REACT_APP_SERVER_ADDRESS}:${process.env.REACT_APP_CONNECTION_PORT}/api/v1/${serviceName}`
    });
}
