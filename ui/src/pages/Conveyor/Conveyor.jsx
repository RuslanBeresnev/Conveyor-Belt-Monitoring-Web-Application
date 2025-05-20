import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import ParamsAndStatusCard from "./ParamsAndStatusCard";

export default function Conveyor() {
    return (
        <Box p={4}>
            <Grid container spacing={4}>
                <Grid item size={2}>
                    <ParamsAndStatusCard />
                </Grid>
            </Grid>
        </Box>
    );
}
