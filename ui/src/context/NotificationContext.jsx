import {createContext, useContext, useState} from "react";

const NotificationContext = createContext();

export function NotificationProvider({ children }) {
    const [title, setTitle] = useState("New notification!");
    const [message, setMessage] = useState("");
    const [open, setOpen] = useState(false);

    const showNotification = (title, message) => {
        setTitle(title);
        setMessage(message);
        setOpen(true);
    };

    const closeNotification = () => {
        setOpen(false);
    }

    return (
        <NotificationContext.Provider value={{ title, message, open, showNotification, closeNotification }}>
            {children}
        </NotificationContext.Provider>
    );
}

export const useNotification = () => useContext(NotificationContext);
