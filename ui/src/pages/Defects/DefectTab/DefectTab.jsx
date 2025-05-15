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

export default function DefectTab({ open, handleClose, defect }) {
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
                    </Grid>
                </Grid>
            </Box>
        </Dialog>
    );
};
