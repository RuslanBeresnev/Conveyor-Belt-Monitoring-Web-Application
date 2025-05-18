import {useEffect, useState} from "react";
import {useError} from "../../context/ErrorContext";
import DefectInfoService from "../../API/DefectInfoService";
import DefectTable from "./DefectTable";
import Filters from "./Filters";
import DefectTab from "./DefectTab/DefectTab";

export default function Defects() {
    const [rows, setRows] = useState([]);
    const {showError} = useError();

    const [tabOpen, setTabOpen] = useState(false);
    const [selectedDefect, setSelectedDefect] = useState(null);

    useEffect(() => {
        DefectInfoService.getAllDefects()
            .then(response => setRows(response.data))
            .catch(error => showError(error, "Table of defects fetching error"));
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
