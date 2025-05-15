import Paper from "@mui/material/Paper";

export default function Photo({base64_photo}) {
    return (
        <Paper
            elevation={3}
            sx={{
                border: '4px solid black',
                maxWidth: '100%',
                justifyContent: 'center',
                alignItems: 'center',
                p: 1,
            }}
        >
            <img
                src={`data:image/png;base64,${base64_photo}`}
                alt="Photo of the defect"
                style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }}
            />
        </Paper>
    )
}
