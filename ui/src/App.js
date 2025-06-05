import {useEffect, useState} from "react";
import {useLocation} from "react-router";
import {Routes, Route} from "react-router-dom";
import {useSSE} from "./hooks/useSSE";
import {appSections} from "./router";
import Topbar from "./components/Topbar/Topbar";
import Sidebar from "./components/Sidebar/Sidebar";
import HealthChecker from "./components/HealthChecker/HealthChecker";
import ErrorDialog from "./components/Dialogs/ErrorDialog";
import NotificationDialog from "./components/Dialogs/NotificationDialog";

export default function App() {
    useSSE();

    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [currentSection, setCurrentSection] = useState('Conveyor Belt Monitoring Web Application');

    const location = useLocation();
    const pathToSectionTitle = {
        '/auth': 'Conveyor Belt Monitoring Web Application',
        '/defects': 'Defects',
        '/conveyor': 'Conveyor',
        '/logs': 'Logs',
        '/settings': 'Settings'
    }

    useEffect(() => {
        setCurrentSection(pathToSectionTitle[location.pathname] || 'Defects');
    }, [location.pathname]);

    return (
        <div className="App">
            <Topbar onMenuClick={() => setSidebarOpen(true)} currentSection={currentSection} />
            <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
            <Routes>
                {appSections.map(route =>
                    <Route path={route.path} key={route.path} element={route.element} exact={route.exact} />
                )}
            </Routes>
            <HealthChecker />
            <ErrorDialog />
            <NotificationDialog />
        </div>
    );
}
