import axios from 'axios';

export default class ConveyorInfoService {
    static getConveyorParameters = async () => {
        try {
            return await axios.get('http://127.0.0.1:8000/api/v1/conveyor_info/parameters');
        } catch (error) {
            throw error;
        }
    }

    static getConveyorStatus = async () => {
        try {
            return await axios.get('http://127.0.0.1:8000/api/v1/conveyor_info/status');
        } catch (error) {
            throw error;
        }
    }

    static changeConveyorParameters = async (new_belt_length, new_belt_width, new_belt_thickness) => {
        try {
            return await axios.post('http://127.0.0.1:8000/api/v1/conveyor_info/change_parameters',
                {"new_belt_length": new_belt_length, "new_belt_width": new_belt_width, "new_belt_thickness": new_belt_thickness});
        } catch (error) {
            throw error;
        }
    }
}
