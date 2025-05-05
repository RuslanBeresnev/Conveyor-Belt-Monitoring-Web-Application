import * as React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';

export default function Defects() {
    const createRow = (id, type, criticality, timestamp) => {
        return { id, type, criticality, timestamp };
    }

    const testRows = [
        createRow(1, 'Tear', 'normal-level', '01.01.2025 - 00:01'),
        createRow(2, 'Delamination', 'normal-level', '01.01.2025 - 00:02'),
        createRow(3, 'Hole', 'extreme-level', '01.01.2025 - 00:03'),
        createRow(4, 'Tear', 'critical-level', '01.01.2025 - 00:04'),
        createRow(5, 'Wear', 'normal-level', '01.01.2025 - 00:05'),
        createRow(6, 'Wear', 'normal-level', '01.01.2025 - 00:06'),
        createRow(7, 'Wear', 'normal-level', '01.01.2025 - 00:07'),
        createRow(8, 'Wear', 'normal-level', '01.01.2025 - 00:08'),
        createRow(9, 'Wear', 'normal-level', '01.01.2025 - 00:09'),
        createRow(10, 'Wear', 'normal-level', '01.01.2025 - 00:10'),
    ];

    const getCriticalityColor = (level) => {
        switch (level) {
            case 'critical-level':
                return 'error.main';
            case 'extreme-level':
                return 'warning.main';
            case 'normal-level':
            default:
                return 'text.primary';
        }
    };

    return (
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
                    {testRows.map((row) => (
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
                            <TableCell align="left">{row.timestamp}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}
