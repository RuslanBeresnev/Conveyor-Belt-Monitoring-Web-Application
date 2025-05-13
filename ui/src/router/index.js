import Defects from "../pages/Defects/Defects";
import Conveyor from "../pages/Conveyor";
import Logs from "../pages/Logs";
import Settings from "../pages/Settings";

export const appSections = [
    {path: '/defects', element: <Defects />, exact: true},
    {path: '/conveyor', element: <Conveyor />, exact: true},
    {path: '/logs', element: <Logs />, exact: true},
    {path: '/settings', element: <Settings />, exact: true},
    {path: "*", element: <Defects />, exact: true}
]
