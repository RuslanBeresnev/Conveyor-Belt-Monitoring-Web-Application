import {Navigate} from "react-router-dom";
import {useAuth} from "../../context/AuthenticationContext";

export default function ProtectedRoute({ children }) {
    const { checkAuth, logout } = useAuth();

    if (!checkAuth()) {
        logout(false);
        return <Navigate to="/auth" replace />;
    }

    return children;
}
