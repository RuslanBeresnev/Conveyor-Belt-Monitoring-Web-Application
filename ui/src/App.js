import {useEffect, useState} from "react";
import {useLocation} from "react-router";
import {Routes, Route} from "react-router-dom";
import {appSections} from "./router";
import Topbar from "./components/Topbar/Topbar";
import Sidebar from "./components/Sidebar/Sidebar";

export default function App() {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [currentSection, setCurrentSection] = useState('');

    const location = useLocation();
    const pathToSectionTitle = {
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
        </div>
    );
}
