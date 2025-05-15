export default class DefectInfoUtils {
    static formatTimestamp = (isoTimestamp) => {
        const date = new Date(isoTimestamp);
        const formattedDate = date.toLocaleDateString('ru-RU');
        const formattedTime = date.toLocaleTimeString('ru-RU');
        return `${formattedDate} - ${formattedTime}`;
    };

    static getCriticalityColor = (level) => {
        switch (level) {
            case 'critical':
                return 'error.main';
            case 'extreme':
                return 'warning.main';
            case 'normal':
            default:
                return 'text.primary';
        }
    };
}
