import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import NetflixHome from "./components/NetflixHome";
import { Toaster } from "./components/ui/sonner";
import { AuthProvider } from "./contexts/AuthContext";

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<NetflixHome />} />
          </Routes>
          <Toaster />
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
}

export default App;