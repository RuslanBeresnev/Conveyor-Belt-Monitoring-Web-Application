import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import TableViewIcon from "@mui/icons-material/TableView";
import ReportService from "../../../API/ReportService";

export default function DownloadReportButtons({defect_id, setError}) {
    const downloadReport = async (report_type) => {
        try {
            await ReportService.downloadReportOfDefect(defect_id, report_type);
        } catch (error) {
            setError(error);
        }
    }

    return (
        <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
            <Button variant='outlined' startIcon={<PictureAsPdfIcon />} color='error' onClick={() => downloadReport('pdf')}>
                PDF
            </Button>
            <Button variant='outlined' startIcon={<TableViewIcon />} color='primary' onClick={() => downloadReport('csv')}>
                CSV
            </Button>
        </Box>
    );
};
