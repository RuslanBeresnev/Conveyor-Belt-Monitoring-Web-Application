import {useNavigate, useLocation} from "react-router";
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import NewReleasesIcon from '@mui/icons-material/NewReleases';
import ConveyorBeltIcon from '@mui/icons-material/ConveyorBelt';
import EventNoteIcon from '@mui/icons-material/EventNote';
import SettingsIcon from '@mui/icons-material/Settings';

export default function Sidebar({open, setOpen}) {
    const navigate = useNavigate();
    const location = useLocation();

    const transitToSection = (path) => {
        setOpen(false)
        navigate(path)
    }

    const buttons = [
        { title: 'Defects', icon: <NewReleasesIcon />, path: '/defects' },
        { title: 'Conveyor', icon: <ConveyorBeltIcon />, path: '/conveyor' },
        { title: 'Logs', icon: <EventNoteIcon />, path: '/logs' },
        { title: 'Settings', icon: <SettingsIcon />, path: '/settings' }
    ];

    const DrawerList = (
        <Box sx={{width: 200}} role="presentation">
            <List>
                {buttons.map(({title, icon, path}) => {
                    const isActive = location.pathname === path;
                    return (
                        <ListItem key={title} disablePadding>
                            <ListItemButton onClick={() => transitToSection(path)} selected={isActive}>
                                <ListItemIcon>
                                    {icon}
                                </ListItemIcon>
                                <ListItemText primary={title}/>
                            </ListItemButton>
                        </ListItem>
                    );
                })}
            </List>
        </Box>
    );

    return (
        <div>
            <Drawer open={open} onClose={() => setOpen(false)}>
                {DrawerList}
            </Drawer>
        </div>
    );
}
