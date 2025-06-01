import TableCell from "@mui/material/TableCell";
import Box from "@mui/material/Box";
import NewReleasesIcon from "@mui/icons-material/NewReleases";

export default function CustomCell({cell, colIndex}) {
            {cell !== null && (
                <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                    <NewReleasesIcon
                        color={
                            cell.criticality === 'critical'
                                ? 'error'
                                : cell.criticality === 'extreme'
                                    ? 'warning'
                                    : 'disabled'
                        }
                    />
                </Box>

            )}
        </TableCell>
    )
}
