import {useEffect, useState} from "react";
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
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
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import DefectInfoService from "../../../API/DefectInfoService";

export default function DefectTab({ open, handleClose, setError, defect, setSelectedDefect, setRows }) {
    const [chainOfPrevious, setChainOfPrevious] = useState([]);
    const [deletionDialogOpen, setDeletionDialogOpen] = useState(false);

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

    const setNewCriticalityOfDefect = async (criticality) => {
        try {
            switch (criticality) {
                case 'critical':
                    await DefectInfoService.setNewCriticalityOfDefect(defect.id, false, true);
                    break;
                case 'extreme':
                    await DefectInfoService.setNewCriticalityOfDefect(defect.id, true, false);
                    break;
                case 'normal':
                    await DefectInfoService.setNewCriticalityOfDefect(defect.id, false, false);
                    break;
                default:
                    return;
            }
            const updatedDefect = { ...defect, criticality };
            setSelectedDefect(updatedDefect);
            setRows(prevRows => prevRows.map(row => row.id === updatedDefect.id ? updatedDefect : row));
        } catch (error) {
            setError(error);
        }
    }

    const deleteDefect = async () => {
        try {
            setDeletionDialogOpen(false);
            await DefectInfoService.deleteDefect(defect.id);
            setRows(prevRows => prevRows.filter(row => row.id !== defect.id));
            handleClose();
        } catch (error) {
            setError(error);
        }
    }

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

            <Box sx={{ p: 4, pb: 2 }}>
                <Grid container spacing={4}>
                    <Grid item size={6}>
                        <Photo base64_photo={defect.base64_photo} />
                        <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                            <FormControl variant="outlined" sx={{ minWidth: 200 }} size='small'>
                                <InputLabel>Set New Criticality</InputLabel>
                                <Select
                                    label="Set New Criticality"
                                    onChange={event => setNewCriticalityOfDefect(event.target.value)}
                                >
                                    <MenuItem value="normal">Normal</MenuItem>
                                    <MenuItem value="extreme">Extreme</MenuItem>
                                    <MenuItem value="critical">Critical</MenuItem>
                                </Select>
                            </FormControl>
                            <IconButton
                                sx={{ ml: 2 }}
                                color="error"
                                onClick={() => setDeletionDialogOpen(true)}
                            >
                                <DeleteForeverIcon fontSize="large" />
                            </IconButton>
                            <Dialog
                                open={deletionDialogOpen}
                                onClose={() => setDeletionDialogOpen(false)}
                            >
                                <DialogTitle>
                                    Confirm deletion
                                </DialogTitle>
                                <DialogContent>
                                    <DialogContentText>
                                        Delete defect with ID = {defect.id}?
                                    </DialogContentText>
                                </DialogContent>
                                <DialogActions>
                                    <Button onClick={() => setDeletionDialogOpen(false)}>Cancel</Button>
                                    <Button onClick={deleteDefect} color="error" variant="contained">
                                        Delete
                                    </Button>
                                </DialogActions>
                            </Dialog>
                        </Box>
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
