import {useEffect, useState} from "react";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import {Alert} from "@mui/material";
import DefectInfoService from "../API/DefectInfoService";

export default function Defects() {
    const [rows, setRows] = useState([]);
    const [error, setError] = useState(null);

    const loadRows = async () => {
        try {
            const response = await DefectInfoService.getAllDefects();
            setRows(response.data);
            setError(null);
        } catch (error) {
            setError(error);
        }
    };

    useEffect(() => {
        loadRows();
    }, []);

    const formatTimestamp = (isoTimestamp) => {
        const date = new Date(isoTimestamp);
        const formattedDate = date.toLocaleDateString('ru-RU');
        const formattedTime = date.toLocaleTimeString('ru-RU');
        return `${formattedDate} - ${formattedTime}`;
    };

    const getCriticalityColor = (level) => {
        switch (level) {
            case 'critical':
                return 'error.main';
            case 'extreme':
                return 'warning.main';
            case 'normal':
            default:
                return 'text.primary';
        }
    };

    return (
        <>
            {error ? (
                <Alert severity="error" sx={{ marginTop: 1, border: '1px solid red', paddingY: '10px' }}>
                    {error.name}: {error.message}
                </Alert>
            ) : (
                <TableContainer component={Paper} sx={{ marginTop: 1 }}>
                    <Table sx={{ minWidth: 850 }}>
                        <TableHead>
                            <TableRow sx={{ '& th': { fontWeight: 'bold' } }}>
                                <TableCell>ID</TableCell>
                                <TableCell align="left">Type</TableCell>
                                <TableCell align="left">Criticality</TableCell>
                                <TableCell align="left">Timestamp</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {rows.map((row) => (
                                <TableRow
                                    key={row.id}
                                    hover
                                    sx={{
                                        '&:last-child td, &:last-child th': { border: 0 },
                                        '& td, & th': {color: getCriticalityColor(row.criticality)}
                                    }}
                                >
                                    <TableCell component="th" scope="row">
                                        {row.id}
                                    </TableCell>
                                    <TableCell align="left">{row.type}</TableCell>
                                    <TableCell  align="left">{row.criticality}</TableCell>
                                    <TableCell align="left">{formatTimestamp(row.timestamp)}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}
        </>
    );
}
