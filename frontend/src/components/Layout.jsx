import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const userName = localStorage.getItem('userName') || 'User';

  function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
    navigate('/login');
  }

  const navItems = [
    { path: '/', label: 'Home', icon: '📊' },
    { path: '/transactions', label: 'Gastos', icon: '💰' },
    { path: '/upload', label: 'Upload', icon: '📤' },
    { path: '/invoices', label: 'Faturas', icon: '📁' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20 md:pb-0">
      {/* Desktop Navbar */}
      <nav className="hidden md:block bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="text-xl font-bold text-indigo-600">
              📊 Invoice Analysis
            </Link>
            <div className="flex gap-4">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`transition ${
                    location.pathname === item.path
                      ? 'text-indigo-600 font-medium'
                      : 'text-gray-600 hover:text-indigo-600'
                  }`}
                >
                  {item.icon} {item.label}
                </Link>
              ))}
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

      {/* Mobile Header */}
      <div className="md:hidden bg-white shadow-sm border-b px-4 py-3 flex items-center justify-between sticky top-0 z-50">
        <span className="text-lg font-bold text-indigo-600">📊 Invoice</span>
        <button
          onClick={handleLogout}
          className="text-sm text-red-500"
        >
          Sair
        </button>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-4 md:py-6">
        <Outlet />
      </main>

      {/* Mobile Bottom Nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg z-50">
        <div className="flex justify-around py-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center py-1 px-3 rounded-lg transition ${
                location.pathname === item.path
                  ? 'text-indigo-600'
                  : 'text-gray-400'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="text-xs mt-0.5">{item.label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
}
