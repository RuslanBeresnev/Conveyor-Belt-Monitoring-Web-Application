import { useEffect, useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import { useError } from "../../../context/ErrorContext";
import BeltProfileTable from "./BeltProfileTable";
import DefectInfoService from "../../../API/DefectInfoService";
import ZoomSlider from "./ZoomSlider";

export default function Infographics({ conveyorParams }) {
    const [defects, setDefects] = useState([]);
    const { showError } = useError();

    const [areaWidth, setAreaWidth] = useState(0);
    const [areaHeight, setAreaHeight] = useState(0);

    const rows = 10;
    const [cols, setCols] = useState(50);

    const [xLabelsEveryNCells, setXLabelsEveryNCells] = useState(3);
    const [yLabelsEveryNCells, setYLabelsEveryNCells] = useState(2);

    const [beltCells, setBeltCells] = useState(
        Array.from({ length: rows }, () => Array(cols).fill(null))
    );

    const fetchInfographicsInfo = () => {
        DefectInfoService.getAllDefects()
            .then(response => setDefects(response.data))
            .catch(error => showError(error, "Belt infographics: defects fetching error"));
    }

    const markCellsWithDefects = async () => {
        const calculatedAreaWidth = conveyorParams.length / cols;
        const calculatedAreaHeight = conveyorParams.width / rows;
        setAreaWidth(calculatedAreaWidth);
        setAreaHeight(calculatedAreaHeight);

        const updatedBeltCells = Array.from({ length: rows }, () => Array(cols).fill(null));
        defects.forEach(defect => {
            // Division by 1 000 000 and by 1 000 necessary because defect's position counted in millimeters
            const x = Math.floor((defect.longitudinal_position / 1000000) / calculatedAreaWidth);
            const y = Math.floor((defect.transverse_position / 1000) / calculatedAreaHeight);
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
    }

    useEffect(fetchInfographicsInfo, []);

    useEffect(() => {
        const conveyorParamsNotNull = conveyorParams.length > 0 && conveyorParams.width > 0 && conveyorParams.thickness > 0;
        if (defects.length === 0 || !conveyorParamsNotNull) return;
        markCellsWithDefects();
    }, [cols, defects, conveyorParams]);

    return (
        <Card variant='outlined'>
            <CardContent>
                <Typography variant='h6'>
                    Belt Profile Infographics
                </Typography>
                <BeltProfileTable
                    beltCells={beltCells}
                    areaWidth={areaWidth}
                    areaHeight={areaHeight}
                    cols={cols}
                    xLabelsEveryNCells={xLabelsEveryNCells}
                    yLabelsEveryNCells={yLabelsEveryNCells}
                />
                <ZoomSlider
                    cols={cols}
                    setCols={setCols}
                    setXLabelsEveryNCells={setXLabelsEveryNCells}
                />
            </CardContent>
        </Card>
    );
}
