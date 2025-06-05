import {createContext, useContext, useState} from 'react';
import AuthenticationUtils from "../utils/AuthenticationUtils";

export const AuthenticationContext = createContext();

export function AuthenticationProvider({ children }) {
    const [authenticated, setAuthenticated] = useState(AuthenticationUtils.checkAuth());

    const login = (token) => {
        AuthenticationUtils.login(token);
        setAuthenticated(true);
    }

    const logout = (redirectToAuth = true) => {
        AuthenticationUtils.logout(redirectToAuth);
        setAuthenticated(false);
    }

    return (
        <AuthenticationContext.Provider value={{ authenticated, checkAuth: AuthenticationUtils.checkAuth, login, logout }}>
            {children}
        </AuthenticationContext.Provider>
    );
}

export const useAuth = () => useContext(AuthenticationContext);
