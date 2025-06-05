import { Navigate } from "react-router-dom";
import Authentication from "../pages/Authentication/Authentication";
import Defects from "../pages/Defects/Defects";
import Conveyor from "../pages/Conveyor/Conveyor";
import Logs from "../pages/Logs/Logs";
import Settings from "../pages/Settings/Settings";
import ProtectedRoute from "../components/ProtectedRoute/ProtectedRoute";

export const appSections = [
    {path: '/auth', element: <Authentication />, exact: true},
    {path: '/defects', element: <ProtectedRoute><Defects /></ProtectedRoute>, exact: true},
    {path: '/conveyor', element: <ProtectedRoute><Conveyor /></ProtectedRoute>, exact: true},
    {path: '/logs', element: <ProtectedRoute><Logs /></ProtectedRoute>, exact: true},
    {path: '/settings', element: <ProtectedRoute><Settings /></ProtectedRoute>, exact: true},
    {path: "*", element: <Navigate to="/defects" replace />, exact: true}
]
