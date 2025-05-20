import {useEffect, useState} from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import {useError} from "../../context/ErrorContext";
import DefectInfoService from "../../API/DefectInfoService";

export default function DefectCountCard() {
    const [defectsCount, setDefectsCount] = useState({ total: 0, extreme: 0, critical: 0  });
    const {showError} = useError();

    useEffect(() => {
        DefectInfoService.getCountOfDefectCriticalityGroups()
            .then(response =>
                setDefectsCount({
                    total: response.data.total,
                    extreme: response.data.extreme,
                    critical: response.data.critical
                }))
            .catch(error => showError(error, "Defect counts by criticality groups fetching error"));
    }, []);

    return (
        <Card variant="outlined">
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    Defects Summary
                </Typography>
                <Box display="flex" flexDirection="column" gap={1}>
                    <Chip label={`Total Count: ${defectsCount.total}`} />
                    <Chip label={`Critical-Level: ${defectsCount.critical}`} color="error" />
                    <Chip label={`Extreme-Level: ${defectsCount.extreme}`} color="warning" />
                </Box>
            </CardContent>
        </Card>
    )
}
