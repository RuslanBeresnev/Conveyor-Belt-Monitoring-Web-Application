import {useState} from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import PictureAsPdfIcon from "@mui/icons-material/PictureAsPdf";
import TableViewIcon from "@mui/icons-material/TableView";
import {useError} from "../../context/ErrorContext";
import ReportService from "../../API/ReportService";

export default function DownloadReportButtons({currentSection}) {
    const [disableButtons, setDisableButtons] = useState(false);
    const {showError} = useError();

    const downloadReport = async (report_type) => {
        setDisableButtons(true);
        setTimeout(() => setDisableButtons(false), 3000);
        try {
            if (currentSection === "Defects") {
                await ReportService.downloadReportOfAllDefects(report_type);
            } else if (currentSection === "Conveyor") {
                await ReportService.downloadReportOfConveyorStateAndParameters(report_type);
            }
        } catch (error) {
            showError(error, "Report downloading error");
        }
    }

    return (
        <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
                variant='contained'
                startIcon={<PictureAsPdfIcon />}
                color='error'
                onClick={() => downloadReport('pdf')}
                disabled={disableButtons}
            >
                PDF
            </Button>
            <Button
                variant='contained'
                startIcon={<TableViewIcon />}
                color='secondary'
                onClick={() => downloadReport('csv')}
                disabled={disableButtons}
            >
                CSV
            </Button>
        </Box>
    );
};
