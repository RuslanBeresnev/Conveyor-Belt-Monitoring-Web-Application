import { useEffect } from 'react';
import {useError} from "../../context/ErrorContext";
import MaintenanceService from "../../API/MaintenanceService";
import {useAuth} from "../../context/AuthenticationContext";

export default function HealthChecker() {
    const { showError } = useError();
    const { authenticated } = useAuth();

    const checkServerAndDatabaseHealth = () => {
        MaintenanceService.checkServer()
            .then(() => MaintenanceService.checkDatabase()
                .catch(error => showError(error, "DATABASE UNAVAILABLE")))
            .catch(error => {showError(error, "SERVER UNAVAILABLE"); return null;});
    }

    useEffect(() => {
        if (!authenticated) return;

        const interval = setInterval(checkServerAndDatabaseHealth, 10000);
        return () => clearInterval(interval);
    }, [authenticated]);

    return null;
};
