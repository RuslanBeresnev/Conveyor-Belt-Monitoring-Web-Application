import TableContainer from "@mui/material/TableContainer";
import Paper from "@mui/material/Paper";
import {Table, TableBody, TableCell, TableRow} from "@mui/material";
import CustomCell from "./CustomCell";

export default function BeltProfileTable({beltCells, areaWidth, areaHeight, cols, xLabelsEveryNCells, yLabelsEveryNCells}) {
    return (
        <TableContainer component={Paper} elevation={0} sx={{ marginTop: 2 }}>
            <Table
                sx={{
                    borderCollapse: 'collapse',
                    tableLayout: 'fixed',
                    '& td:not(.axis-x):not(.axis-y):not(.corner-cell), & th:not(.axis-x):not(.axis-y):not(.corner-cell)': {
                        border: '1px solid rgba(0, 0, 0, 0.12)',
                        textAlign: 'center',
                        verticalAlign: 'middle',
                        padding: 0
                    },
                    '& td, & th': {
                        width: 30,
                        height: 25,
                    }
                }}
            >
                <TableBody>
                    {beltCells.slice().reverse().map((row, rowIndex) => {
                        const originalRowIndex = beltCells.length - 1 - rowIndex;
                        return (
                            <TableRow key={originalRowIndex}>
                                <TableCell
                                    className="axis-y"
                                    key={`y-label-${originalRowIndex}`}
                                    sx={{
                                        border: 'none',
                                        borderBottom:
                                            originalRowIndex % yLabelsEveryNCells === 0
                                                ? '1px solid rgba(0, 0, 0, 0.12)'
                                                : 'none',
                                        backgroundColor: 'transparent',
                                        fontSize: 12,
                                        fontWeight: 500,
                                        padding: '0 4px',
                                        textAlign: 'right',
                                        verticalAlign: 'bottom'
                                    }}
                                >
                                    {
                                        originalRowIndex % yLabelsEveryNCells === 0
                                        ? (originalRowIndex * areaHeight).toFixed(2)
                                        : ""
                                    }
                                </TableCell>
                                {row.map((cell, colIndex) => (
                                    <CustomCell key={colIndex} cell={cell} />
                                ))}
                            </TableRow>
                        );
                    })}
                    <TableRow>
                        <TableCell
                            className="corner-cell"
                            sx={{
                                border: 'none',
                                fontSize: 12,
                                fontWeight: 500,
                                padding: 0,
                                textAlign: 'center',
                                verticalAlign: 'middle'
                            }}
                        >
                            Y(m) / X(km)
                        </TableCell>
                        {Array.from({ length: cols }).map((_, colIndex) => (
                            <TableCell
                                className="axis-x"
                                key={`x-label-${colIndex}`}
                                sx={{
                                    border: 'none',
                                    borderLeft:
                                        colIndex % xLabelsEveryNCells === 0
                                            ? '1px solid rgba(0, 0, 0, 0.12)'
                                            : 'none',
                                    backgroundColor: 'transparent',
                                    fontSize: 12,
                                    fontWeight: 500,
                                    padding: '2px 0',
                                    textAlign: 'left',
                                    verticalAlign: 'top'
                                }}
                            >
                                {
                                    colIndex % xLabelsEveryNCells === 0
                                    ? (colIndex * areaWidth).toFixed(2)
                                    : ""
                                }
                            </TableCell>
                        ))}
                    </TableRow>
                </TableBody>
            </Table>
        </TableContainer>
    );
}
