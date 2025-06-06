import {createContext, useContext, useState} from "react";

const ErrorContext = createContext();

export function ErrorProvider({ children }) {
    const [title, setTitle] = useState("Error");
    const [error, setError] = useState(null);
    const [open, setOpen] = useState(false);

    const showError = (error, title) => {
        // If server has returned HTTP 401 status-code then error will not display because application instantly
        // will redirect to /auth route
        if (error.response?.status === 401) return;
        setError(error);
        setTitle(title);
        setOpen(true);
    };

    const closeError = () => {
        setOpen(false);
    }

    const handleError = () => {
        setError(null);
    }

    return (
        <ErrorContext.Provider value={{ error, title, open, showError, closeError, handleError }}>
            {children}
        </ErrorContext.Provider>
    );
}

export const useError = () => useContext(ErrorContext);
