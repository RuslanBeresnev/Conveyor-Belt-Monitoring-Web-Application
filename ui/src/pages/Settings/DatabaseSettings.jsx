import {useState, useRef} from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import {useError} from "../../context/ErrorContext";
import ConfirmationDialog from "./ConfirmationDialog";
import MaintenanceService from "../../API/MaintenanceService";

export default function DatabaseSettings() {
    const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
    const [dialogTitle, setDialogTitle] = useState("Title")
    const [dialogText, setDialogText] = useState("Text");
    const [confirmButtonText, setConfirmButtonText] = useState("Confirm");
    const onConfirm = useRef(() => {});

    const [disableButton, setDisableButton] = useState(false);

    const {showError} = useError();

    const recreateDatabase = async () => {
        MaintenanceService.recreateDatabase()
            .catch(error => showError(error, "Database recreation error"));
    };

    const fillDatabaseWithRequiredData = async () => {
        MaintenanceService.fillDatabaseWithRequiredData()
            .catch(error => showError(error, "Database data filling error"));
    };

    const addTestDefectToDatabase = async () => {
        setDisableButton(true);
        try {
            await MaintenanceService.addTestDefectToDatabase();
        } catch (error) {
            showError(error, "Adding test defect error");
        } finally {setDisableButton(false)}
    };

    return (
        <>
            <Card>
                <CardContent>
                    <Typography variant='h6' gutterBottom>
                        Database Settings
                    </Typography>
                    <Stack direction='row' spacing={2}>
                        <Button
                            variant='outlined'
                            color='error'
                            onClick={() => {
                                setDialogTitle("Confirm database recreation");
                                setDialogText("Are you sure you want to recreate database? " +
                                    "All tables will be create from scratch and all current data will be lost.");
                                setConfirmButtonText("Recreate DB");
                                onConfirm.current = recreateDatabase;
                                setConfirmDialogOpen(true);
                            }}
                        >
                            Recreate DB
                        </Button>
                        <Button
                            variant='outlined'
                            color='error'
                            onClick={() => {
                                setDialogTitle("Confirm database filling");
                                setDialogText("Are you sure you want to fill database with required data? " +
                                    "This operation should only be performed after the database has been recreated.");
                                setConfirmButtonText("Fill DB");
                                onConfirm.current = fillDatabaseWithRequiredData;
                                setConfirmDialogOpen(true);
                            }}
                        >
                            Fill DB
                        </Button>
                        <Button
                            variant='outlined'
                            disabled={disableButton}
                            onClick={addTestDefectToDatabase}
                        >
                            Add test defect
                        </Button>
                    </Stack>
                </CardContent>
            </Card>
            <ConfirmationDialog
                open={confirmDialogOpen}
                setOpen={setConfirmDialogOpen}
                onConfirm={onConfirm}
                confirmButtonText={confirmButtonText}
                title={dialogTitle}
                text={dialogText}
            />
        </>
    )
}
