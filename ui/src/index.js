import React from 'react';
import ReactDOM from 'react-dom/client';
import {BrowserRouter} from "react-router";
import App from './App';
import {ErrorProvider} from "./context/ErrorContext";
import {NotificationProvider} from "./context/NotificationContext";
import {AuthenticationProvider} from "./context/AuthenticationContext";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <AuthenticationProvider>
        <NotificationProvider>
            <ErrorProvider>
                <BrowserRouter>
                    <App />
                </BrowserRouter>
            </ErrorProvider>
        </NotificationProvider>
    </AuthenticationProvider>
);
