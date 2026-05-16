import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { Phone, BarChart2, LayoutDashboard, LogOut } from "lucide-react";
import { useAuthStore } from "../store/authStore";
import { authApi } from "../api/client";
import clsx from "clsx";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { to: "/call", label: "Aktif Çağrı", icon: Phone },
  { to: "/reports", label: "Raporlar", icon: BarChart2 },
];

export default function Layout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await authApi.logout().catch(() => {});
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-gray-950">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold text-brand-500">CallMate AI</h1>
          <p className="text-xs text-gray-500 mt-1">Çağrı Merkezi Asistanı</p>
        </div>

        <nav className="flex-1 px-3 pb-4 space-y-1">
          {nav.map(({ to, label, icon: Icon, exact }) => (
            <NavLink
              key={to}
              to={to}
              end={exact}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-brand-600 text-white"
                    : "text-gray-400 hover:bg-gray-800 hover:text-gray-100"
                )
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <div className="text-sm text-gray-400 mb-2 truncate">{user?.full_name ?? "Demo Kullanıcı"}</div>
          <div className="text-xs text-gray-600 mb-3 truncate">{user?.email ?? "demo@callmate.ai"}</div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-red-400 transition-colors"
          >
            <LogOut size={16} /> Çıkış Yap
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
