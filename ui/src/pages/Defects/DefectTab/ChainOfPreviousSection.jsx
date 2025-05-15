import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";

export default function ChainOfPreviousSection({chainOfPrevious, setSelectedDefect}) {
    return (
        <Box sx={{ mt: 1 }}>
            {chainOfPrevious.length > 0 &&
                <Typography variant='body2' sx={{ mb: 1 }}>
                    <strong>Previous variations in defect progression chain:</strong>
                </Typography>
            }
            <Box>
                {chainOfPrevious.map(defect => (
                    <Button
                        key={defect.id}
                        variant='outlined'
                        sx={{ mr: 1 }}
                        onClick={() => setSelectedDefect(defect)}
                    >
                        id = {defect.id}
                    </Button>
                ))}
            </Box>
        </Box>
    )
}
