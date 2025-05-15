import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";

export default function DefectAppBar({defectId, handleClose}) {
    return (
        <AppBar sx={{ position: 'relative', backgroundColor: 'black' }}>
            <Toolbar>
                <Typography sx={{ ml: 2, flex: 1 }} variant='h6' component='div'>
                    DEFECT INFO (ID = {defectId})
                </Typography>
                <IconButton edge='end' color='inherit' onClick={handleClose}>
                    <CloseIcon />
                </IconButton>
            </Toolbar>
        </AppBar>
    );
}
