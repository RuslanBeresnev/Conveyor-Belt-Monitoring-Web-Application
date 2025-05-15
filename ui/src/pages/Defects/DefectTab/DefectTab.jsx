import {useEffect, useState} from "react";
import Dialog from '@mui/material/Dialog';
import Slide from '@mui/material/Slide';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import InfoTable from "./InfoTable";
import Photo from "./Photo";
import Button from "@mui/material/Button";
import DefectInfoService from "../../../API/DefectInfoService";

export default function DefectTab({ open, handleClose, defect, setSelectedDefect, setError }) {
    const [chainOfPrevious, setChainOfPrevious] = useState([]);

    const getChainOfPreviousDefects = async (id) => {
        try {
            const response = await DefectInfoService.getChainOfPreviousDefectVariationsByDefectId(id);
            if (response.status !== 404) {
                setChainOfPrevious(response.data);
            }
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
        <Dialog fullScreen open={open} onClose={handleClose} slots={{ transition: Slide }}
                slotProps={{ transition: { direction: 'up' } }}>
            <AppBar sx={{ position: 'relative', backgroundColor: 'black' }}>
                <Toolbar>
                    <Typography sx={{ ml: 2, flex: 1 }} variant='h6' component='div'>
                        DEFECT INFO (ID = {defect.id})
                    </Typography>
                    <IconButton edge='end' color='inherit' onClick={handleClose}>
                        <CloseIcon />
                    </IconButton>
                </Toolbar>
            </AppBar>

            <Box sx={{ p: 4 }}>
                <Grid container spacing={4}>
                    <Grid item size={6}>
                        <Photo base64_photo={defect.base64_photo} />
                    </Grid>
                    <Grid item size={6}>
                        <InfoTable defect={defect} />
                        <Box sx={{ mt: 1 }}>
                            {chainOfPrevious.length > 0 &&
                                <Typography variant='body2' sx={{ mb: 1 }}>
                                    <strong>Previous variations in defect progression chain:</strong>
                                </Typography>
                            }
                            <Box>
                                {chainOfPrevious.map(defect => (
                                    <Button
                                        key={defect.id}
                                        variant='outlined'
                                        sx={{ mr: 1 }}
                                        onClick={() => setSelectedDefect(defect)}
                                    >
                                        id = {defect.id}
                                    </Button>
                                ))}
                            </Box>
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </Dialog>
    );
};
