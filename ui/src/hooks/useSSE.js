import { useEffect } from "react";
import {useError} from "../context/ErrorContext";
import {useNotification} from "../context/NotificationContext";

export const useSSE = () => {
    const {showError} = useError();
    const { showNotification } = useNotification();

    useEffect(() => {
        const eventSource = new EventSource("http://localhost:8000/api/v1/maintenance/get_events");

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                showNotification(data.title, data.text);
            } catch (error) {
                showError(error, "Server-sent events (SSE) data parsing error. This was probably a notification " +
                    "about a new defect. Check the \"Defects\" section.");
            }
        };

        eventSource.onerror = (error) => {
            showError(error, "Some server-sent events (SSE) error. This was probably a notification about a new " +
                "defect. Check the \"Defects\" section.");
            eventSource.close();
        };

        return () => {
            eventSource.close();
        };
    }, []);
};
