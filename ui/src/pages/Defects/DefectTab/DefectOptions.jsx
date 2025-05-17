import {useState} from "react";
import Box from "@mui/material/Box";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import IconButton from "@mui/material/IconButton";
import {useError} from "../../../context/ErrorContext";
import DefectInfoService from "../../../API/DefectInfoService";

export default function DefectOptions({defect, setSelectedDefect, setRows, handleClose}) {
    const [deletionDialogOpen, setDeletionDialogOpen] = useState(false);
    const {showError} = useError();

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
            showError(error, "Criticality changing error");
        }
    }

    const deleteDefect = async () => {
        try {
            setDeletionDialogOpen(false);
            await DefectInfoService.deleteDefect(defect.id);
            setRows(prevRows => prevRows.filter(row => row.id !== defect.id));
            handleClose();
        } catch (error) {
            showError(error, "Defect deletion error");
        }
    }

    return (
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
    )
}
