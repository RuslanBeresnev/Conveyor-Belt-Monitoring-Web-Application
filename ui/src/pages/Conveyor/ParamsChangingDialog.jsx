import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import TextField from "@mui/material/TextField";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import {useError} from "../../context/ErrorContext";
import ConveyorInfoService from "../../API/ConveyorInfoService";

export default function ParamsChangingDialog({setParams, editedParams, setEditedParams, open, setOpen}) {
    const {showError} = useError();

    const handleSaveNewParams = async () => {
        setOpen(false);
        try {
            // Converting parameters from kilometers and meters to millimeters
            await ConveyorInfoService.changeConveyorParameters(
                Math.trunc(editedParams.length * 1000000),
                Math.trunc(editedParams.width * 1000),
                Math.trunc(editedParams.thickness * 1)
            )
            setParams(editedParams);
        } catch (error) {
            showError(error, "Conveyor parameters changing error");
        }
    };

    return (
        <Dialog open={open} onClose={() => setOpen(false)}>
            <DialogTitle>Change Conveyor Parameters</DialogTitle>
            <DialogContent>
                <TextField
                    fullWidth
                    margin="dense"
                    label="Belt Length (km)"
                    type="number"
                    value={editedParams.length}
                    onChange={e => setEditedParams({ ...editedParams, length: parseFloat(e.target.value) })}
                />
                <TextField
                    fullWidth
                    margin="dense"
                    label="Belt Width (m)"
                    type="number"
                    value={editedParams.width}
                    onChange={e => setEditedParams({ ...editedParams, width: parseFloat(e.target.value) })}
                />
                <TextField
                    fullWidth
                    margin="dense"
                    label="Belt Thickness (mm)"
                    type="number"
                    value={editedParams.thickness}
                    onChange={e => setEditedParams({ ...editedParams, thickness: parseFloat(e.target.value) })}
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={() => setOpen(false)}>Cancel</Button>
                <Button onClick={handleSaveNewParams} variant="contained">Save</Button>
            </DialogActions>
        </Dialog>
    )
}
