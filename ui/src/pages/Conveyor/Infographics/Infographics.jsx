import { useEffect, useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import { useError } from "../../../context/ErrorContext";
import BeltProfileTable from "./BeltProfileTable";
import DefectInfoService from "../../../API/DefectInfoService";
import ConveyorInfoService from "../../../API/ConveyorInfoService";

export default function Infographics() {
    const { showError } = useError();

    const [areaWidth, setAreaWidth] = useState(0);
    const [areaHeight, setAreaHeight] = useState(0);

    const rows = 10;
    const cols = 50;

    const [beltCells, setBeltCells] = useState(
        Array.from({ length: rows }, () => Array(cols).fill(null))
    );

    const markCellsWithDefects = async () => {
        try {
            const defectsResponse = await DefectInfoService.getAllDefects();
            const defects = defectsResponse.data;

            const paramsResponse = await ConveyorInfoService.getConveyorParameters();
            const calculatedAreaWidth = paramsResponse.data.belt_length / cols;
            const calculatedAreaHeight = paramsResponse.data.belt_width / rows;
            setAreaWidth(calculatedAreaWidth);
            setAreaHeight(calculatedAreaHeight);

            const updatedBeltCells = beltCells.map(row => [...row]);
            defects.forEach(defect => {
                const x = Math.floor(defect.longitudinal_position / calculatedAreaWidth);
                const y = Math.floor(defect.transverse_position / calculatedAreaHeight);
                if (updatedBeltCells[y] && updatedBeltCells[y][x] !== undefined) {
                    const cellValue = updatedBeltCells[y][x];
                    if (cellValue === null) {
                        updatedBeltCells[y][x] = defect;
                    } else if (Array.isArray(cellValue)) {
                        updatedBeltCells[y][x] = [...cellValue, defect];
                    } else {
                        updatedBeltCells[y][x] = [cellValue, defect];
                    }
                }
            });
            setBeltCells(updatedBeltCells);
        } catch (error) {
            showError(error, "Infographics information fetching error");
        }
    }

    useEffect(() => {
        markCellsWithDefects();
    }, []);

    return (
        <Card variant="outlined">
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    Belt Profile Infographics
                </Typography>
                <BeltProfileTable
                    beltCells={beltCells}
                    areaWidth={areaWidth}
                    areaHeight={areaHeight}
                    cols={cols}
                />
            </CardContent>
        </Card>
    );
}
