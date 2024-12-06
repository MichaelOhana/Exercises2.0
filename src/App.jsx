import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import CoursePage from './pages/CoursePage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/course" element={<CoursePage />} />
      </Routes>
    </Router>
  );
}

export default App; 