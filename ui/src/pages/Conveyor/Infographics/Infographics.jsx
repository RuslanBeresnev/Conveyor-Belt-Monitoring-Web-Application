import {useEffect, useState} from "react";
import TableContainer from "@mui/material/TableContainer";
import Paper from "@mui/material/Paper";
import {Table} from "@mui/material";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import CustomCell from "./CustomCell";
import {useError} from "../../../context/ErrorContext";
import DefectInfoService from "../../../API/DefectInfoService";
import ConveyorInfoService from "../../../API/ConveyorInfoService";

export default function Infographics() {
    const {showError} = useError();

    const rows = 10;
    const cols = 50;

    const [beltCells, setBeltCells] = useState(
        Array.from({ length: rows }, () => Array(cols).fill(null))
    );

    const markCellsWithDefects = async () => {
        try {
            const defectsResponse = await DefectInfoService.getAllDefects();
            const defects = defectsResponse.data;

            const paramsResponse = await ConveyorInfoService.getConveyorParameters();
            const realCellWidth = paramsResponse.data.belt_length / cols;
            const realCellHeight = paramsResponse.data.belt_width / rows;

            const updatedBeltCells = beltCells.map(row => [...row]);
            defects.forEach(defect => {
                const x = Math.floor(defect.longitudinal_position / realCellWidth);
                const y = Math.floor(defect.transverse_position / realCellHeight);
                if (updatedBeltCells[y] && updatedBeltCells[y][x] !== undefined) {
                    const cellValue = updatedBeltCells[y][x];
                    if (cellValue === null) {
                        updatedBeltCells[y][x] = defect;
                    } else if (Array.isArray(cellValue)) {
                        updatedBeltCells[y][x] = [...cellValue, defect];
                    } else {
                        updatedBeltCells[y][x] = [cellValue, defect];
                    }
                }
            });
            setBeltCells(updatedBeltCells);
        } catch (error) {
            showError(error, "Infographics information fetching error");
        }
    }

    useEffect(() => {
        markCellsWithDefects();
    },[]);

    return (
        <TableContainer component={Paper} sx={{ marginTop: 4 }}>
            <Table
                sx={{
                    borderCollapse: 'collapse',
                    tableLayout: 'fixed',
                    '& td, & th': {
                        border: '1px solid rgba(0, 0, 0, 0.12)',
                        width: 30,
                        height: 25,
                        textAlign: 'center',
                        verticalAlign: 'middle',
                        padding: 0
                    }
                }}
            >
                <TableBody>
                    {beltCells.map((row, rowIndex) => (
                        <TableRow key={rowIndex}>
                            {row.map((cell, colIndex) =>
                                <CustomCell key={colIndex} cell={cell} />
                            )}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    )
};
