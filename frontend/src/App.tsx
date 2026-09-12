import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Signup from './pages/Signup';
import EmployerDashboard from './pages/EmployerDashboard';
import EmployeeDashboard from './pages/EmployeeDashboard';
import RankingPage from './pages/RankingPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/employer" element={<EmployerDashboard />} />
        <Route path="/employer/jobs/:id" element={<RankingPage />} />
        <Route path="/employee" element={<EmployeeDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
