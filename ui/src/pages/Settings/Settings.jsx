import Box from "@mui/material/Box";
import NotificationSettings from "./NotificationSettings";

export default function Settings() {
    return (
        <Box p={4} display='flex' flexDirection='column' gap={4}>
            <NotificationSettings />
        </Box>
    );
}
