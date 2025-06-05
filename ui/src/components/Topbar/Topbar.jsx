import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from "@mui/material/Button";
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import LogoutIcon from '@mui/icons-material/Logout';
import {useAuth} from "../../context/AuthenticationContext";
import DownloadReportButtons from "./DownloadReportButtons";

export default function Topbar({onMenuClick, currentSection}) {
    const { logout } = useAuth();

    return (
        <Box sx={{flexGrow: 1}}>
            <AppBar position='static'>
                <Toolbar>
                    {(currentSection !== 'Conveyor Belt Monitoring Web Application') &&
                        <IconButton
                            size='large'
                            edge='start'
                            color='inherit'
                            aria-label='menu'
                            sx={{mr: 2}}
                            onClick={onMenuClick}
                        >
                            <MenuIcon/>
                        </IconButton>
                    }

                    <Typography variant='h6' component='div' sx={{flexGrow: 1}}>
                        {currentSection}
                    </Typography>

                    {(currentSection === 'Defects' || currentSection === 'Conveyor') &&
                        <DownloadReportButtons currentSection={currentSection} />
                    }

                    {(currentSection !== 'Conveyor Belt Monitoring Web Application') &&
                        <Button
                            sx={{ ml: 2 }}
                            startIcon={<LogoutIcon />}

                            color='inherit'
                            onClick={() => logout()}
                        >
                            Logout
                        </Button>
                    }
                </Toolbar>
            </AppBar>
        </Box>
    );
}
