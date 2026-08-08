import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { MobileHeader } from './components/MobileHeader';
import { Footer } from './components/Footer';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { NewAnalysisPage } from './pages/NewAnalysisPage';
import { AnalysisProgressPage } from './pages/AnalysisProgressPage';
import { ReportPage } from './pages/ReportPage';
import { ProjectsPage } from './pages/ProjectsPage';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen flex flex-col md:flex-row bg-slate-950 text-slate-100 selection:bg-cyan-500 selection:text-white overflow-x-hidden">
        <MobileHeader />
        <Sidebar />
        <div className="flex-1 flex flex-col justify-between min-w-0">
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/landing" element={<LandingPage />} />
              <Route path="/new" element={<NewAnalysisPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/analysis/:jobId" element={<AnalysisProgressPage />} />
              <Route path="/report/:jobId" element={<ReportPage />} />
              <Route path="/insights" element={<DashboardPage />} />
              <Route path="/settings" element={<ProjectsPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </div>
    </Router>
  );
};

export default App;
