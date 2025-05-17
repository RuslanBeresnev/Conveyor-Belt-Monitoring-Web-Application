import { useEffect } from 'react';
import {useError} from "../../context/ErrorContext";
import MaintenanceService from "../../API/MaintenanceService";

export default function HealthChecker() {
    const {showError} = useError();

    const checkServerAndDatabaseHealth = async() => {
        try {
            await MaintenanceService.checkServer();
        } catch (error) {
            showError(error, "SERVER UNAVAILABLE");
            return;
        }
        try {
            await MaintenanceService.checkDatabase();
        } catch (error) {
            showError(error, "DATABASE UNAVAILABLE");
        }
    }

    useEffect(() => {
        const interval = setInterval(checkServerAndDatabaseHealth, 10000);
        return () => clearInterval(interval);
    }, []);

    return null;
};
