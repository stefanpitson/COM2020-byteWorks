import { Navigate } from 'react-router-dom';

interface Props {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: Props) {
  const token = localStorage.getItem('token');
  const isAuth = localStorage.getItem('loggedIn') === 'true';

  // If there's no token, they aren't logged in
  if (!token || !isAuth) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}