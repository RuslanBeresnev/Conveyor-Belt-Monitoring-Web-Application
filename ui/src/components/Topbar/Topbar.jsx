import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import DownloadReportButtons from "./DownloadReportButtons";

export default function Topbar({onMenuClick, currentSection}) {
    return (
        <Box sx={{flexGrow: 1}}>
            <AppBar position="static">
                <Toolbar>
                    <IconButton
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="menu"
                        sx={{mr: 2}}
                        onClick={onMenuClick}
                    >
                        <MenuIcon/>
                    </IconButton>
                    <Typography variant="h6" component="div" sx={{flexGrow: 1}}>
                        {currentSection}
                    </Typography>
                    <>
                        {(currentSection === 'Defects' || currentSection === 'Conveyor') &&
                            <DownloadReportButtons currentSection={currentSection} />
                        }
                    </>
                </Toolbar>
            </AppBar>
        </Box>
    );
}
