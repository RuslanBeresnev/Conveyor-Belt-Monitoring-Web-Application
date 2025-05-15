import TableContainer from "@mui/material/TableContainer";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import TableBody from "@mui/material/TableBody";
import DefectInfoUtils from "../../../utils/DefectInfoUtils";

export default function InfoTable({defect}) {
    return (
        <TableContainer component={Paper} sx={{ mb: 4 }}>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell><strong>Parameter</strong></TableCell>
                        <TableCell><strong>Value</strong></TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    <TableRow>
                        <TableCell>Defect Type</TableCell>
                        <TableCell>{defect.type}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>{DefectInfoUtils.formatTimestamp(defect.timestamp)}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Defect On Belt</TableCell>
                        <TableCell>{defect.is_on_belt ? 'true' : 'false'}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Box Size (mm)</TableCell>
                        <TableCell>{defect.box_length_in_mm} x {defect.box_width_in_mm}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Position (X: m, Y: cm)</TableCell>
                        <TableCell>
                            X={parseInt(defect.longitudinal_position / 1000) + ' '}
                            Y={parseInt(defect.transverse_position / 10)}
                        </TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Probability</TableCell>
                        <TableCell>{defect.probability}%</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Criticality</TableCell>
                        <TableCell
                            sx={{
                                color: DefectInfoUtils.getCriticalityColor(defect.criticality),
                                fontWeight: 'bold'
                            }}
                        >
                            {defect.criticality.toUpperCase()}
                        </TableCell>
                    </TableRow>
                </TableBody>
            </Table>
        </TableContainer>
    )
}
