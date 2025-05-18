import {useState} from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import TableViewIcon from "@mui/icons-material/TableView";
import {useError} from "../../../context/ErrorContext";
import ReportService from "../../../API/ReportService";

export default function DownloadReportButtons({defect_id}) {
    const [disableButtons, setDisableButtons] = useState(false);
    const {showError} = useError();

    const downloadReport = async (report_type) => {
        setDisableButtons(true);
        try {
            await ReportService.downloadReportOfDefect(defect_id, report_type);
        } catch (error) {
            showError(error, "Report about defect downloading error");
        } finally {setDisableButtons(false)}
    }

    return (
        <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
            <Button
                variant='outlined'
                startIcon={<PictureAsPdfIcon />}
                color='error'
                onClick={() => downloadReport('pdf')}
                disabled={disableButtons}
            >
                PDF
            </Button>
            <Button
                variant='outlined'
                startIcon={<TableViewIcon />}
                color='primary'
                onClick={() => downloadReport('csv')}
                disabled={disableButtons}
            >
                CSV
            </Button>
        </Box>
    );
};
