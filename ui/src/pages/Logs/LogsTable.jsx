import { useState } from 'react';
import Table from '@mui/material/Table';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import TableBody from '@mui/material/TableBody';
import Paper from '@mui/material/Paper';
import IconButton from '@mui/material/IconButton';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import NewReleasesIcon  from '@mui/icons-material/NewReleases';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import InfoIcon from '@mui/icons-material/Info';
import ReportIcon from '@mui/icons-material/Report';
import CloseFullscreenIcon from '@mui/icons-material/CloseFullscreen';
import DescriptionIcon from '@mui/icons-material/Description';
import EmailIcon from '@mui/icons-material/Email';
import ConveyorBeltIcon from '@mui/icons-material/ConveyorBelt';
import {useError} from "../../context/ErrorContext";
import DefectInfoUtils from "../../utils/DefectInfoUtils";
import LoggingService from '../../API/LoggingService';
import DeletionDialog from "./DeletionDialog";

const logTypeIcons = {
    error: <ReportIcon color="error" />,
    warning: <WarningAmberIcon sx={{ color: '#fbcb2d' }} />,
    info: <InfoIcon color="info" />,
    critical_defect: <NewReleasesIcon color="error" />,
    extreme_defect: <NewReleasesIcon color="warning" />,
    action_info: <CloseFullscreenIcon sx={{ color: '#9900ff' }} />,
    report_info: <DescriptionIcon sx={{ color: '#607d8b' }} />,
    message: <EmailIcon color="primary" />,
    state_of_devices: <ConveyorBeltIcon sx={{ color: '#535353' }} />
};

export default function LogsTable({ setRows, filteredLatestRows }) {
    const [logIdToDelete, setLogIdToDelete] = useState(0);
    const [deletionDialogOpen, setDeletionDialogOpen] = useState(false);
    const {showError} = useError();

    const deleteLog = async (needToLog) => {
        setRows(previousRows => previousRows.filter((row) => row.id !== logIdToDelete));
        setDeletionDialogOpen(false);
        LoggingService.deleteLogById(logIdToDelete, needToLog).catch(error => showError(error, "Log record deletion error"));
    };

    return (
        <>
            <TableContainer component={Paper} sx={{ marginTop: 1 }}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell sx={{ fontWeight: 'bold' }}>Icon</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Log</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Type</TableCell>
                            <TableCell sx={{ fontWeight: 'bold' }}>Timestamp</TableCell>
                            <TableCell />
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {filteredLatestRows.map(log => (
                            <TableRow key={log.id}>
                                <TableCell>{logTypeIcons[log.type]}</TableCell>
                                <TableCell style={{ whiteSpace: 'pre-wrap', maxWidth: 400 }}>
                                    {log.text}
                                </TableCell>
                                <TableCell>{log.type.toUpperCase()}</TableCell>
                                <TableCell>{DefectInfoUtils.formatTimestamp(log.timestamp)}</TableCell>
                                <TableCell align="center">
                                    <IconButton
                                        color="error"
                                        onClick={() => {setLogIdToDelete(log.id); setDeletionDialogOpen(true);}}
                                    >
                                        <DeleteOutlineIcon />
                                    </IconButton>
                                </TableCell>
                            </TableRow>
                        ))}
                        {filteredLatestRows.length === 0 && (
                            <TableRow>
                                <TableCell colSpan={5} align="center">
                                    No logs available
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
            <DeletionDialog
                open={deletionDialogOpen}
                setOpen={setDeletionDialogOpen}
                onDelete={deleteLog}
                title="Delete log"
                text="Are you sure you want to delete this log record?"
            />
        </>
    );
}
