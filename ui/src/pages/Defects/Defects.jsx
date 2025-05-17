import {useEffect, useState} from "react";
import DefectInfoService from "../../API/DefectInfoService";
import DefectTable from "./DefectTable";
import Filters from "./Filters";
import DefectTab from "./DefectTab/DefectTab";
import {useError} from "../../context/ErrorContext";

export default function Defects() {
    const [rows, setRows] = useState([]);
    const {showError} = useError();

    const [tabOpen, setTabOpen] = useState(false);
    const [selectedDefect, setSelectedDefect] = useState(null);

    const loadRows = async () => {
        try {
            const response = await DefectInfoService.getAllDefects();
            setRows(response.data);
        } catch (error) {
            showError(error, "Table of defects fetching error");
        }
    };

    useEffect(() => {
        loadRows();
    }, []);

    return (
        <>
            <Filters setRows={setRows} />
            <DefectTable rows={rows} setTabOpen={setTabOpen} setSelectedDefect={setSelectedDefect} />
            <DefectTab
                open={tabOpen}
                handleClose={() => setTabOpen(false)}
                defect={selectedDefect}
                setSelectedDefect={setSelectedDefect}
                setRows={setRows}
            />
        </>
    );
}
