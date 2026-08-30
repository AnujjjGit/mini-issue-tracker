import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { api } from "./api/client.js";
import { useAuth } from "./auth/AuthContext.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Login from "./pages/Login.jsx";
import ProjectPage from "./pages/ProjectPage.jsx";
import Register from "./pages/Register.jsx";

function Header(){const {isAuthenticated,email,logout}=useAuth();const navigate=useNavigate();async function handleLogout(){try{await api.logout();}catch{} logout();navigate("/login");}if(!isAuthenticated)return null;return <header className="app-header"><Link to="/" className="brand">Mini Issue Tracker</Link><div className="header-right"><span data-testid="current-user" className="current-user">{email}</span><button data-testid="logout-button" onClick={handleLogout}>Logout</button></div></header>}

export default function App(){return <div className="app"><Header/><main className="content"><Routes><Route path="/login" element={<Login/>}/><Route path="/register" element={<Register/>}/><Route path="/" element={<ProtectedRoute><Dashboard/></ProtectedRoute>}/><Route path="/projects/:projectId" element={<ProtectedRoute><ProjectPage/></ProtectedRoute>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes></main></div>}
