import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { LandingPage } from './pages/LandingPage';
import { NewAnalysisPage } from './pages/NewAnalysisPage';
import { AnalysisProgressPage } from './pages/AnalysisProgressPage';
import { ReportPage } from './pages/ReportPage';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen flex flex-col justify-between bg-slate-950 text-slate-100 selection:bg-cyan-500 selection:text-white">
        <div>
          <Navbar />
          <main>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/new" element={<NewAnalysisPage />} />
              <Route path="/analysis/:jobId" element={<AnalysisProgressPage />} />
              <Route path="/report/:jobId" element={<ReportPage />} />
            </Routes>
          </main>
        </div>
        <Footer />
      </div>
    </Router>
  );
};

export default App;
