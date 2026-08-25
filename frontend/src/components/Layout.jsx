import { Outlet, Link, useNavigate } from 'react-router-dom';

export default function Layout() {
  const navigate = useNavigate();
  const userName = localStorage.getItem('userName') || 'User';

  function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
    navigate('/login');
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="text-xl font-bold text-indigo-600">
              📊 Invoice Analysis
            </Link>
            <div className="flex gap-4">
              <Link to="/" className="text-gray-600 hover:text-indigo-600 transition">
                Dashboard
              </Link>
              <Link to="/upload" className="text-gray-600 hover:text-indigo-600 transition">
                Upload
              </Link>
              <Link to="/invoices" className="text-gray-600 hover:text-indigo-600 transition">
                Faturas
              </Link>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">Olá, {userName}</span>
            <button
              onClick={handleLogout}
              className="text-sm text-red-500 hover:text-red-700 transition"
            >
              Sair
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
