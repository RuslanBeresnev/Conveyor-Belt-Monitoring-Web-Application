import {useEffect, useRef, useState} from 'react'
import {Typography} from "@mui/material";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Checkbox from "@mui/material/Checkbox";
import TelegramIcon from "@mui/icons-material/Telegram";
import EmailIcon from "@mui/icons-material/Email";
import {useError} from "../../context/ErrorContext";
import MaintenanceService from "../../API/MaintenanceService";
import NotificationService from "../../API/NotificationService";

export default function NotificationSettings() {
    const [onNewDefectTelegramChecked, setOnNewDefectTelegramChecked] = useState(true);
    const [onNewDefectGmailChecked, setOnNewDefectGmailChecked] = useState(true);
    const [sendReportTelegramChecked, setSendReportTelegramChecked] = useState(true);
    const [sendReportGmailChecked, setSendReportGmailChecked] = useState(true);

    const {showError} = useError();

    const isInitialized = useRef(false);

    const [disableButtons, setDisableButtons] = useState(false);

    useEffect(() => {
        MaintenanceService.getUserNotificationSettings()
            .then(response => {
                const { new_defect_notification_scope, report_sending_scope } = response.data;

                setOnNewDefectTelegramChecked(new_defect_notification_scope.includes('Telegram'));
                setOnNewDefectGmailChecked(new_defect_notification_scope.includes('Gmail'));
                setSendReportTelegramChecked(report_sending_scope.includes('Telegram'));
                setSendReportGmailChecked(report_sending_scope.includes('Gmail'));

                isInitialized.current = true;
            })
            .catch(error => showError(error, 'User notification settings fetching error'));
    }, []);

    useEffect(() => {
        if (!isInitialized.current) return;

        const onNewDefectNotificationScope = [];
        const reportSendingScope = [];

        if (onNewDefectTelegramChecked) onNewDefectNotificationScope.push('Telegram');
        if (onNewDefectGmailChecked) onNewDefectNotificationScope.push('Gmail');
        if (sendReportTelegramChecked) reportSendingScope.push('Telegram');
        if (sendReportGmailChecked) reportSendingScope.push('Gmail');

        MaintenanceService.updateUserNotificationSettings(onNewDefectNotificationScope, reportSendingScope)
            .catch(error => showError(error, 'User notification settings updating error'));
    }, [onNewDefectTelegramChecked, onNewDefectGmailChecked, sendReportTelegramChecked, sendReportGmailChecked]);

    const sendTelegramNotification = async (message) => {
        setDisableButtons(true)
        try {
            await NotificationService.sendTelegramNotification(message)
        } catch (error) {
            showError(error, 'Telegram notification sending error')
        } finally {setDisableButtons(false)}
    }

    const sendGmailNotification = async (subject, text) => {
        setDisableButtons(true)
        try {
            await NotificationService.sendGmailNotification(subject, text)
        } catch (error) {
            showError(error, 'Gmail notification sending error')
        } finally {setDisableButtons(false)}
    }

    return (
        <Card>
            <CardContent>
                <Typography variant='h6' gutterBottom>
                    Notification Settings
                </Typography>
                <Stack spacing={2}>
                    <Box display='flex' alignItems='center' gap={2}>
                        <Typography sx={{ minWidth: 180 }}>On new defect</Typography>
                        <Checkbox
                            icon={<TelegramIcon />}
                            checkedIcon={<TelegramIcon color='primary' />}
                            checked={onNewDefectTelegramChecked}
                            onChange={event => setOnNewDefectTelegramChecked(event.target.checked)}
                        />
                        <Checkbox
                            icon={<EmailIcon />}
                            checkedIcon={<EmailIcon color='primary' />}
                            checked={onNewDefectGmailChecked}
                            onChange={event => setOnNewDefectGmailChecked(event.target.checked)}
                        />
                    </Box>
                    <Box display='flex' alignItems='center' gap={2}>
                        <Typography sx={{ minWidth: 180 }}>Send reports</Typography>
                        <Checkbox
                            icon={<TelegramIcon />}
                            checkedIcon={<TelegramIcon color='primary' />}
                            checked={sendReportTelegramChecked}
                            onChange={event => setSendReportTelegramChecked(event.target.checked)}
                        />
                        <Checkbox
                            icon={<EmailIcon />}
                            checkedIcon={<EmailIcon color='primary' />}
                            checked={sendReportGmailChecked}
                            onChange={event => setSendReportGmailChecked(event.target.checked)}
                        />
                    </Box>
                    <Box display='flex' gap={2}>
                        <Button
                            variant='outlined'
                            onClick={() => sendTelegramNotification('Test notification from client!')}
                            disabled={disableButtons}
                        >
                            Send test TG-message
                        </Button>
                        <Button
                            variant='outlined'
                            onClick={() => sendGmailNotification('Test letter', 'Test notification from client!')}
                            disabled={disableButtons}
                        >
                            Send test Gmail-letter
                        </Button>
                    </Box>
                </Stack>
            </CardContent>
        </Card>
    )
}
