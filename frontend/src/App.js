import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import PatientDetail from './pages/PatientDetail';
import ChatSession from './pages/ChatSession';
import NewPatient from './pages/NewPatient';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="sidebar">
          <div className="sidebar-brand">
            <h2>Medbridge</h2>
            <span className="subtitle">Health Coach</span>
          </div>
          <ul className="nav-links">
            <li>
              <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>
                Dashboard
              </NavLink>
            </li>
            <li>
              <NavLink to="/patients/new" className={({ isActive }) => isActive ? 'active' : ''}>
                New Patient
              </NavLink>
            </li>
          </ul>
          <div className="sidebar-footer">
            <span className="version">v1.0.0</span>
          </div>
        </nav>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/patients/new" element={<NewPatient />} />
            <Route path="/patients/:id" element={<PatientDetail />} />
            <Route path="/patients/:id/chat" element={<ChatSession />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
