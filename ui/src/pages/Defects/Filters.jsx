import {useState} from 'react';
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import DefectInfoService from "../../API/DefectInfoService";

export default function Filters({setRows, setError}) {
    const types = [
        'chip', 'delamination', 'rope', 'crack', 'liftup', 'hole', 'tear', 'wear', 'joint', 'joint_worn'
    ];
    const [type, setType] = useState('');

    const onFilterChange = async (event) => {
        try {
            setType(event.target.value);
            const response = await DefectInfoService.getFilteredDefects(event.target.value);
            setRows(response.data);
        } catch (error) {
            setError(error);
        }
    }

    return (
        <FormControl sx={{ marginTop: '15px', marginBottom: '10px', minWidth: 100 }} size='small'>
            <InputLabel>Type</InputLabel>
            <Select
                variant='outlined'
                value={type}
                label='Type'
                onChange={onFilterChange}
            >
                <MenuItem value='all'>All</MenuItem>
                {types.map(type => (
                    <MenuItem value={type}>{type}</MenuItem>
                ))}
            </Select>
        </FormControl>
    );
};
