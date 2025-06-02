import Typography from "@mui/material/Typography";
import Slider from "@mui/material/Slider";
import {Grid} from "@mui/material";

export default function ZoomSlider({cols, setCols, setXLabelsEveryNCells}) {
    const marks = [10, 20, 30, 40, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
        .map(value => ({ value, label: String(value) }));

    const rerenderTable = (event, newValue) => {
        setCols(newValue);
        if (newValue === 10 || newValue === 20) setXLabelsEveryNCells(1);
        if (newValue === 30 || newValue === 40) setXLabelsEveryNCells(2);
        if (newValue >= 50) setXLabelsEveryNCells(3);
    }

    return (
        <Grid container sx={{mt: 2}}>
            <Grid item size={0.35}>
                <Typography variant="overline">
                    Zoom
                </Typography>
            </Grid>
            <Grid item size={11.65}>
                <Slider
                    value={cols}
                    defaultValue={50}
                    size='small'
                    valueLabelDisplay='off'
                    marks={marks}
                    min={10}
                    max={500}
                    step={null}
                    onChange={rerenderTable}
                />
            </Grid>
        </Grid>
    )
}
