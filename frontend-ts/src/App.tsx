import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Login2 from './pages/Login2'
import Home from './pages/Home'
import './App.css'
import api from './api'
import ProtectedRoute from './components/ProtectedRoute'
import MainLayout from './components/MainLayout'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/home" replace />} />
        <Route path="/login" element={<Login />} />
        <Route element={<MainLayout />}>
          <Route path="/home" element={<Home />}/>
        </Route>
        
        <Route path="/login2" element={<Login2 />}/>
      </Routes>
    </BrowserRouter>
  )
}
 