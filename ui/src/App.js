import {useState} from "react";
import Topbar from "./components/Topbar/Topbar";
import Sidebar from "./components/Sidebar/Sidebar";
import {BrowserRouter} from "react-router";
import {Routes, Route} from "react-router-dom";
import {appSections} from "./router";

export default function App() {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [currentSection, setCurrentSection] = useState('Defects');

    return (
        <div className="App">
            <BrowserRouter>
                <Topbar onMenuClick={() => setSidebarOpen(true)} currentSection={currentSection} />
                <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} setCurrentSection={setCurrentSection} />
                <Routes>
                    {appSections.map(route =>
                        <Route path={route.path} key={route.path} element={route.element} exact={route.exact} />
                    )}
                </Routes>
            </BrowserRouter>
        </div>
    );
}
