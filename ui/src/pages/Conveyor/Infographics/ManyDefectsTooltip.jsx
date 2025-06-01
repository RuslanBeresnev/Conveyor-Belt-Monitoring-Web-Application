import Tooltip from "@mui/material/Tooltip";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Zoom from "@mui/material/Zoom";
import {useEffect} from "react";

export default function ManyDefectsTooltip({children, cellContent}) {
    return (
        <Tooltip
            title={
                <Box sx={{ p: 1, minWidth: 200 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        Many Defects In Area!
                    </Typography>
                    <Typography variant="body2">Count: {cellContent.length}</Typography>
                    <Typography variant="body2">IDs:{cellContent.map(defect => ` ${defect.id}`)}</Typography>
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
