import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import {useNotification} from "../../context/NotificationContext";

export default function NotificationDialog() {
    const {title, message, open, closeNotification} = useNotification();

    return (
        <Dialog open={open} onClose={closeNotification}>
            <DialogTitle>
                {title}
            </DialogTitle>
            <DialogContent>
                <DialogContentText dangerouslySetInnerHTML={{ __html: message.replace(/\n/g, '<br>') }} />
            </DialogContent>
            <DialogActions>
                <Button onClick={closeNotification}>OK</Button>
            </DialogActions>
        </Dialog>
    )
}
