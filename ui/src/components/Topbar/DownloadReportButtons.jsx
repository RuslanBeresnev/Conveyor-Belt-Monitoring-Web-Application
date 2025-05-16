import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import TableViewIcon from "@mui/icons-material/TableView";
import ReportService from "../../API/ReportService";

export default function DownloadReportButtons({currentSection}) {
    const downloadReport = async (report_type) => {
        try {
            if (currentSection === "Defects") {
                await ReportService.downloadReportOfAllDefects(report_type);
            } else if (currentSection === "Conveyor") {
                await ReportService.downloadReportOfConveyorStateAndParameters(report_type);
            }
        } catch (error) {
            console.log(error);
        }
    }

    return (
        <Box sx={{ display: 'flex', gap: 2 }}>
            <Button variant='contained' startIcon={<PictureAsPdfIcon />} color='error' onClick={() => downloadReport('pdf')}>
                PDF
            </Button>
            <Button variant='contained' startIcon={<TableViewIcon />} color='secondary' onClick={() => downloadReport('csv')}>
                CSV
            </Button>
        </Box>
    );
};
