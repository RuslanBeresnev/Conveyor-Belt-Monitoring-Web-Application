import {LocalizationProvider} from "@mui/x-date-pickers/LocalizationProvider";
import {AdapterDayjs} from "@mui/x-date-pickers/AdapterDayjs";
import {DatePicker} from "@mui/x-date-pickers/DatePicker";

export default function DateIntervalSelect({fromDate, toDate, setFromDate, setToDate}) {
    return (
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DatePicker
                sx={{ mt: 2, mb: 1, mr: 2 }}
                slotProps={{ textField: { size: 'small' } }}
                format="DD.MM.YYYY"
                label='From Date'
                value={fromDate}
                onChange={(newFromDate) => setFromDate(newFromDate)}
            />
            <DatePicker
                sx={{ mt: 2, mb: 1, mr: 2 }}
                slotProps={{ textField: { size: 'small' } }}
                format="DD.MM.YYYY"
                label='To Date'
                value={toDate}
                onChange={(newToDate) => setToDate(newToDate.hour(23).minute(59).second(59))}
            />
        </LocalizationProvider>
    );
};
