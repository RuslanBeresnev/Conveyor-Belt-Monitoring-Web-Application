import {useEffect, useState} from 'react'
import {Grid} from "@mui/material";
import DefectInfoService from "../../API/DefectInfoService";
import FilterSelect from "./FilterSelect";
import DateIntervalSelect from "./DateIntervalSelect";

export default function Filters({setRows, setError}) {
    const [allTypes, setAllTypes] = useState([])
    const [type, setType] = useState('all');

    const criticalityVariants = ['critical', 'extreme', 'normal']
    const [criticality, setCriticality] = useState('all')

    const [fromDate, setFromDate] = useState(null)
    const [toDate, setToDate] = useState(null)

    useEffect(() => {
        DefectInfoService.getAllTypesOfDefects()
            .then(response => setAllTypes(response.data.types))
            .catch(error => setError(error));
    }, [])

    const onFilterChange = async (event) => {
        try {
            const response = await DefectInfoService.getFilteredDefects(
                type, criticality, fromDate, toDate
            );
            setRows(response.data);
        } catch (error) {
            setError(error);
        }
    }

    useEffect(() => {
        onFilterChange();
    }, [type, criticality, fromDate, toDate]);

    return (
        <Grid container>
            <Grid item>
                <FilterSelect label='Type' value={type} onChange={event => setType(event.target.value)} options={allTypes} />
                <FilterSelect label='Criticality' value={criticality} onChange={event => setCriticality(event.target.value)} options={criticalityVariants} />
            </Grid>
            <Grid item sx={{ marginLeft: 'auto' }}>
                <DateIntervalSelect fromDate={fromDate} toDate={toDate} setFromDate={setFromDate} setToDate={setToDate} />
            </Grid>
        </Grid>
    );
};
