import {useEffect, useState} from 'react';
import DefectInfoService from "../../API/DefectInfoService";
import FilterSelect from "./FilterSelect";

export default function Filters({setRows, setError}) {
    const [allTypes, setAllTypes] = useState([])
    const [type, setType] = useState('all');

    const criticalityVariants = ['critical', 'extreme', 'normal']
    const [criticality, setCriticality] = useState('all')

    useEffect(() => {
        DefectInfoService.getAllTypesOfDefects()
            .then(response => setAllTypes(response.data.types))
            .catch(error => setError(error));
    }, [])

    const onFilterChange = async (event) => {
        try {
            const response = await DefectInfoService.getFilteredDefects(type, criticality);
            setRows(response.data);
        } catch (error) {
            setError(error);
        }
    }

    useEffect(() => {
        onFilterChange();
    }, [type, criticality]);

    return (
        <>
            <FilterSelect label='Type' value={type} onChange={event => setType(event.target.value)} options={allTypes} />
            <FilterSelect label='Criticality' value={criticality} onChange={event => setCriticality(event.target.value)} options={criticalityVariants} />
        </>
    );
};
