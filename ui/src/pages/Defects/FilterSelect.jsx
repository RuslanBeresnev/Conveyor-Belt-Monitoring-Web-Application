import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";

export default function FilterSelect({label, value, options, onChange}) {
    return (
        <FormControl sx={{ marginTop: '15px', marginBottom: '10px', marginRight: '15px', minWidth: 125 }} size='small'>
            <InputLabel>{label}</InputLabel>
            <Select
                variant='outlined'
                value={value}
                label={label}
                onChange={onChange}
            >
                <MenuItem value='all'>All</MenuItem>
                {options.map(option => (
                    <MenuItem value={option}>{option}</MenuItem>
                ))}
            </Select>
        </FormControl>
    );
};
