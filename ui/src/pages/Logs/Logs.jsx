import React, { useEffect, useState } from 'react';
import {useError} from "../../context/ErrorContext";
import LogsTable from './LogsTable';
import LoggingService from '../../API/LoggingService';

export default function Logs() {
    const [rows, setRows] = useState([]);
    const [filteredLatestRows, setFilteredLatestRows] = useState([]);
    const {showError} = useError();

    useEffect(() => {
        LoggingService.getAllLogs()
            .then(response => {
                setRows(response.data);
                setFilteredLatestRows(response.data);
            })
            .catch(error => showError(error, "Log records fetching error"));
    }, []);

    return (
        <>
            <LogsTable
                rows={rows}
                setRows={setRows}
                filteredLatestRows={filteredLatestRows}
                setFilteredLatestRows={setFilteredLatestRows}
            />
        </>
    );
}
