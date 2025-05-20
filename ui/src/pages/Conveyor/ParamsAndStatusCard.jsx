import {useEffect, useState} from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import ConveyorInfoService from "../../API/ConveyorInfoService";
import {useError} from "../../context/ErrorContext";

export default function ParamsAndStatusCard() {
    const [params, setParams] = useState({ length: 0, width: 0, thickness: 0 });
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
            .then(response => {
                if (response.data.is_normal) setStatus("normal")
                else if (response.data.is_extreme) setStatus("extreme")
                else if (response.data.is_critical) setStatus("critical")
            })
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
                <Typography sx={{ mt: 2 }}>
                    Conveyor Status: <Chip label={status} color={statusColor[status]} variant="outlined" />
                </Typography>
            </CardContent>
        </Card>
    );
}
