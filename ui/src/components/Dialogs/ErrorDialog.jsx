import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import {Alert} from "@mui/material";
import {useError} from "../../context/ErrorContext";

export default function ErrorDialog() {
    const {error, title, open, closeError, handleError} = useError();

    return (
        <Dialog open={open} onClose={closeError} onExited={handleError}>
            <DialogTitle>
                {title}
            </DialogTitle>
            <DialogContent>
                <Alert severity='error' sx={{ border: '1px solid red' }}>
                    {error ?
                        <>
                            {`${error.name}: \"${error.message}\"`}
                            {error.response ?
                                <>
                                    <br />
                                    {`Details: \"${error.response.data.detail}\"`}
                                </>
                            : ''}
                        </>
                    : ''
                    }
                </Alert>
            </DialogContent>
            <DialogActions>
                <Button onClick={closeError}>OK</Button>
            </DialogActions>
        </Dialog>
    )
}
