import Box from "@mui/material/Box";
import NotificationSettings from "./NotificationSettings";
import DatabaseSettings from "./DatabaseSettings";

export default function Settings() {
    return (
        <Box p={4} display='flex' flexDirection='column' gap={4}>
            <NotificationSettings />
            <DatabaseSettings />
        </Box>
    );
}
