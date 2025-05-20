import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import ParamsAndStatusCard from "./ParamsAndStatusCard";
import DefectCountCard from "./DefectCountCard";

export default function Conveyor() {
    return (
        <Box p={4}>
            <Grid container spacing={4}>
                <Grid item size={2}>
                    <ParamsAndStatusCard />
                </Grid>
                <Grid item size={2}>
                    <DefectCountCard />
                </Grid>
            </Grid>
        </Box>
    );
}
