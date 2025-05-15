import React from 'react';
import TableContainer from "@mui/material/TableContainer";
import {Table} from "@mui/material";
import Paper from "@mui/material/Paper";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import TableBody from "@mui/material/TableBody";
import DefectInfoUtils from '../../utils/DefectInfoUtils';

export default function DefectTable({ rows, setTabOpen, setSelectedDefect }) {
    const openDefectTab = (defect) => {
        setSelectedDefect(defect);
        setTabOpen(true);
    }

    return (
        <TableContainer component={Paper} sx={{ marginTop: 1 }}>
            <Table sx={{ minWidth: 850 }}>
                <TableHead>
                    <TableRow sx={{ '& th': { fontWeight: 'bold' } }}>
                        <TableCell>ID</TableCell>
                        <TableCell align='left'>Type</TableCell>
                        <TableCell align='left'>Criticality</TableCell>
                        <TableCell align='left'>Timestamp</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {rows.map((row) => (
                        <TableRow
                            key={row.id}
                            hover
                            sx={{
                                '&:last-child td, &:last-child th': { border: 0 },
                                '& td, & th': {color: DefectInfoUtils.getCriticalityColor(row.criticality)}
                            }}
                            onClick={() => openDefectTab(row)}
                        >
                            <TableCell component="th" scope="row">
                                {row.id}
                            </TableCell>
                            <TableCell align='left'>{row.type}</TableCell>
                            <TableCell  align='left'>{row.criticality}</TableCell>
                            <TableCell align='left'>{DefectInfoUtils.formatTimestamp(row.timestamp)}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};
