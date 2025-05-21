import {createServiceApi} from "./BaseAPI";

const api = createServiceApi('conveyor_info')

export default class ConveyorInfoService {
    static getConveyorParameters = async () => await api.get('/parameters')

    static getConveyorStatus = async () => await api.get('/status')

    static changeConveyorParameters = async (new_belt_length, new_belt_width, new_belt_thickness) =>
        await api.post('/change_parameters', {
            "new_belt_length": new_belt_length,
            "new_belt_width": new_belt_width,
            "new_belt_thickness": new_belt_thickness
        })
}
