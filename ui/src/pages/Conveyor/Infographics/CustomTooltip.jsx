import Tooltip from "@mui/material/Tooltip";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Zoom from "@mui/material/Zoom";

export default function CustomTooltip({children, cell}) {
    return (
        <Tooltip
            title={
                <Box sx={{ p: 1, minWidth: 200 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        Defect Info
                    </Typography>
                    <Typography variant="body2">ID: {cell.id}</Typography>
                    <Typography variant="body2">Type: {cell.type}</Typography>
                    <Typography variant="body2">
                        Pos (m, cm):
                        X={Math.floor(cell.longitudinal_position / 1000)},
                        Y={Math.floor(cell.transverse_position / 10)}
                    </Typography>
                    <Typography variant="body2">
                        Size (mm): {cell.box_length_in_mm} x {cell.box_width_in_mm}
                    </Typography>
                </Box>
            }
            arrow
            placement="right"
            slots={{ transition: Zoom }}
        >
            {children}
        </Tooltip>
    )
}
