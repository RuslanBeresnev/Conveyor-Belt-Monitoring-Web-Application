import { useEffect, useState } from 'react';
import Grid from '@mui/material/Grid';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import InputLabel from '@mui/material/InputLabel';
import Button from '@mui/material/Button';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import {useError} from "../../context/ErrorContext";
import DeletionDialog from "./DeletionDialog";
import LoggingService from "../../API/LoggingService";

export default function LogsTableOptions({ rows, setRows, setFilteredLatestRows }) {
    const [filterType, setFilterType] = useState('All');
    const [latestCount, setLatestCount] = useState(10);

    const filterTypes = [
        'error', 'warning', 'info', 'critical_defect', 'extreme_defect',
        'action_info', 'report_info', 'message', 'state_of_devices'
    ]
    const latestCountOptions = [-1, 5, 10, 25, 50, 100];

    const [deletionDialogOpen, setDeletionDialogOpen] = useState(false);
    const {showError} = useError();

    useEffect(() => {
        if (filterType !== 'All') {
            setFilteredLatestRows(rows.filter(log => log.type === filterType));
        } else {
            setFilteredLatestRows(rows);
        }
        if (latestCount !== -1) setFilteredLatestRows(previousRows => previousRows.slice(0, latestCount));
    }, [filterType, latestCount, rows]);

    const deleteAllLogs = async (needToLog) => {
        setRows([]);
        setDeletionDialogOpen(false);
        LoggingService.deleteAllLogs(needToLog).catch(error => showError(error, "All logs deletion error"));
    };

    return (
        <>
            <Grid container alignItems="center" spacing={2} sx={{ mt: 2, mb: 1 }}>
                <Grid item>
                    <FormControl size="small" sx={{ minWidth: 160 }}>
                        <InputLabel>Type</InputLabel>
                        <Select
                            variant="outlined"
                            label="Type"
                            value={filterType}
                            onChange={event => setFilterType(event.target.value)}
                        >
                            <MenuItem value='All'>All</MenuItem>
                            {filterTypes.map(type =>
                                <MenuItem key={type} value={type}>
                                    {type.toUpperCase()}
                                </MenuItem>
                            )}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item>
                    <FormControl size="small" sx={{ minWidth: 140 }}>
                        <InputLabel>Show latest</InputLabel>
                        <Select
                            variant="outlined"
                            label="Show latest"
                            value={latestCount}
                            onChange={event => setLatestCount(event.target.value)}
                        >
                            {latestCountOptions.map(option =>
                                <MenuItem key={option} value={option}>
                                    {option === -1 ? 'All' : option}
                                </MenuItem>
                            )}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item sx={{ ml: 'auto', mr: 2 }}>
                    <Button
                        variant="outlined"
                        color="error"
                        startIcon={<DeleteForeverIcon />}
                        onClick={() => setDeletionDialogOpen(true)}
                    >
                        All
                    </Button>
                </Grid>
            </Grid>
            <DeletionDialog
                open={deletionDialogOpen}
                setOpen={setDeletionDialogOpen}
                onDelete={deleteAllLogs}
                title="Delete all logs"
                text="Are you sure you want to delete ALL log records?"
            />
        </>
    );
}
