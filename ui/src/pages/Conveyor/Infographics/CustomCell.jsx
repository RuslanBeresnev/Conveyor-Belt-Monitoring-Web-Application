import TableCell from "@mui/material/TableCell";
import OneDefectTooltip from "./OneDefectTooltip";
import ManyDefectsTooltip from "./ManyDefectsTooltip";
import Box from "@mui/material/Box";
import NewReleasesIcon from "@mui/icons-material/NewReleases";
import AutoAwesomeMotionIcon from '@mui/icons-material/AutoAwesomeMotion';

export default function CustomCell({cell}) {
    return (
        <TableCell>
            {cell !== null && (
                    <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                        {Array.isArray(cell)
                            ?
                            <ManyDefectsTooltip cellContent={cell} >
                                <AutoAwesomeMotionIcon color='secondary' />
                            </ManyDefectsTooltip>
                            :
                            <OneDefectTooltip cell={cell} >
                                <NewReleasesIcon
                                    color={
                                        cell.criticality === 'critical'
                                            ? 'error'
                                            : cell.criticality === 'extreme'
                                                ? 'warning'
                                                : 'disabled'
                                    }
                                />
                            </OneDefectTooltip>
                        }
                    </Box>
            )}
        </TableCell>
    )
}
