import {useState} from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import {FormControlLabel, Checkbox} from "@mui/material";

export default function DeletionDialog({open, setOpen, onDelete, title, text}) {
    const [logDeletion, setLogDeletion] = useState(true);

    return (
        <Dialog open={open} onClose={() => setOpen(null)}>
            <DialogTitle>{title}</DialogTitle>
            <DialogContent>
                <DialogContentText>{text}</DialogContentText>
                <FormControlLabel
                    control={
                        <Checkbox
                            checked={logDeletion}
                            onChange={event => setLogDeletion(event.target.checked)}
                        />
                    }
                    label="Log deletion event?"
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={() => setOpen(false)}>
                    Cancel
                </Button>
                <Button variant="contained" color="error" onClick={() => onDelete(logDeletion)}>
                    Delete
                </Button>
            </DialogActions>
        </Dialog>
    )
}
