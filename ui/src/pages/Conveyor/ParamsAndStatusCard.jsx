import {useEffect, useState} from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Button from "@mui/material/Button";
import {useError} from "../../context/ErrorContext";
import ConveyorInfoService from "../../API/ConveyorInfoService";

export default function ParamsAndStatusCard({params, setParams, handleOpenParamsChangingDialog}) {

    const [status, setStatus] = useState("normal");
    const {showError} = useError();

    useEffect(() => {
        ConveyorInfoService.getConveyorParameters()
            .then(response => setParams({
                length: response.data.belt_length / 1000000,
                width: response.data.belt_width / 1000,
                thickness: response.data.belt_thickness
            }))
            .catch(error => showError(error, "Conveyor parameters fetching error"));

        ConveyorInfoService.getConveyorStatus()
            .then(response => setStatus(response.data.status))
            .catch(error => showError(error, "Conveyor status fetching error"));
    }, []);

    const statusColor = {
        "normal": "success",
        "extreme": "warning",
        "critical": "error",
    };

    return (
        <Card variant="outlined">
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    Conveyor Parameters
                </Typography>
                <Typography>Belt Length: {params.length} km</Typography>
                <Typography>Belt Width: {params.width} m</Typography>
                <Typography>Belt Thickness: {params.thickness} mm</Typography>
                <Box sx={{ mt: 2 }}>
                    <Typography component="span">Conveyor Status: </Typography>
                    <Chip label={status} color={statusColor[status]} variant="outlined" />
                </Box>
                <Button variant="outlined" sx={{ mt: 3 }} onClick={handleOpenParamsChangingDialog}>
                    Change Parameters
                </Button>
            </CardContent>
        </Card>
    );
}
