import {useState} from "react";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import ParamsAndStatusCard from "./ParamsAndStatusCard";
import DefectCountCard from "./DefectCountCard";
import ParamsChangingDialog from "./ParamsChangingDialog";
import Infographics from "./Infographics/Infographics";

export default function Conveyor() {
    // params.length as kilometers, params.width as meters
    const [params, setParams] = useState({ length: 0, width: 0, thickness: 0 });
    const [editedParams, setEditedParams] = useState({ ...params });
    const [paramsChangeDialogOpen, setParamsChangeDialogOpen] = useState(false);

    const handleOpenParamsChangingDialog = () => {
        setEditedParams({ ...params });
        setParamsChangeDialogOpen(true);
    };

    return (
        <Box p={4}>
            <Grid container spacing={4}>
                <Grid item size={2.5}>
                    <ParamsAndStatusCard
                        params={params}
                        setParams={setParams}
                        handleOpenParamsChangingDialog={handleOpenParamsChangingDialog}
                    />
                </Grid>
                <Grid item size={2.5}>
                    <DefectCountCard />
                </Grid>
                <Grid item size={12}>
                    <Infographics conveyorParams={params} />
                </Grid>
            </Grid>
            <ParamsChangingDialog
                setParams={setParams}
                editedParams={editedParams}
                setEditedParams={setEditedParams}
                open={paramsChangeDialogOpen}
                setOpen={setParamsChangeDialogOpen}
            />
        </Box>
    );
}
