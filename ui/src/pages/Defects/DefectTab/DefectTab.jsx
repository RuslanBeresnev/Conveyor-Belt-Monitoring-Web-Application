import {useEffect, useState} from "react";
import Dialog from '@mui/material/Dialog';
import Slide from '@mui/material/Slide';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import DefectInfoService from "../../../API/DefectInfoService";
import DefectAppBar from "./DefectAppBar";
import DefectInfoTable from "./DefectInfoTable";
import DefectPhoto from "./DefectPhoto";
import DefectOptions from "./DefectOptions";
import ChainOfPreviousSection from "./ChainOfPreviousSection";
import DownloadReportButtons from "./DownloadReportButtons";

export default function DefectTab({ open, handleClose, setError, defect, setSelectedDefect, setRows }) {
    const [chainOfPrevious, setChainOfPrevious] = useState([]);

    const getChainOfPreviousDefects = async (id) => {
        try {
            const response = await DefectInfoService.getChainOfPreviousDefectVariationsByDefectId(id);
            setChainOfPrevious(response.data);
        } catch (error) {
            setError(error);
        }
    };

    useEffect(() => {
        if (!defect) return;
        getChainOfPreviousDefects(defect.id);
    }, [defect]);

    if (!defect) return null;

    return (
        <Dialog
            fullScreen
            open={open}
            onClose={handleClose}
            slots={{ transition: Slide }}
            slotProps={{ transition: { direction: 'up' } }}
        >
            <DefectAppBar defectId={defect.id} handleClose={handleClose} />
            <Box sx={{ p: 4, pb: 2 }}>
                <Grid container spacing={4}>
                    <Grid item size={6}>
                        <DefectPhoto base64_photo={defect.base64_photo} />
                        <DefectOptions
                            defect={defect}
                            setSelectedDefect={setSelectedDefect}
                            setRows={setRows}
                            setError={setError}
                            handleClose={handleClose}
                        />
                    </Grid>
                    <Grid item size={6}>
                        <DefectInfoTable defect={defect} />
                        <ChainOfPreviousSection chainOfPrevious={chainOfPrevious} setSelectedDefect={setSelectedDefect} />
                        <DownloadReportButtons defect_id={defect.id} setError={setError} />
                    </Grid>
                </Grid>
            </Box>
        </Dialog>
    );
};
