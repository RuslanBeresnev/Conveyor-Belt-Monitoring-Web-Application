import {useEffect, useState} from "react";
import {Alert} from "@mui/material";
import DefectInfoService from "../../API/DefectInfoService";
import DefectTable from "./DefectTable";
import Filters from "./Filters";

export default function Defects() {
    const [rows, setRows] = useState([]);
    const [error, setError] = useState(null);

    const loadRows = async () => {
        try {
            const response = await DefectInfoService.getAllDefects();
            setRows(response.data);
            setError(null);
        } catch (error) {
            setError(error);
        }
    };

    useEffect(() => {
        loadRows();
    }, []);

    return (
        <>
            {error ? (
                <Alert severity='error' sx={{ marginTop: 1, border: '1px solid red', paddingY: '10px' }}>
                    {error.name}: {error.message}
                </Alert>
            ) : (
                <>
                    <Filters setRows={setRows} setError={setError} />
                    <DefectTable rows={rows} />
                </>
            )}
        </>
    );
}
