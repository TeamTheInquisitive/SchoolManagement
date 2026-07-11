import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
import { GraduationCap } from 'lucide-react';
import { LoginPage as SharedLoginPage } from 'school-erp-ui-shared';
import { login, clearError } from '../../store/authSlice';

export default function LoginPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { loading, error, user } = useSelector((s) => s.auth);
  const redirectTo = location.state?.from || '/admin';

  // If already authenticated, don't show the login form — go to the app.
  useEffect(() => {
    if (user) navigate(redirectTo, { replace: true });
  }, [user, redirectTo, navigate]);

  const handleSubmit = async (data) => {
    dispatch(clearError());
    const result = await dispatch(login(data));
    if (result.meta.requestStatus === 'fulfilled') {
      navigate(redirectTo, { replace: true });
    }
  };

  return (
    <SharedLoginPage
      title="Admin ERP Portal"
      subtitle="Sign in to access your dashboard"
      icon={GraduationCap}
      gradientFrom="from-indigo-500"
      gradientTo="to-purple-700"
      accentColor="indigo"
      buttonColor="bg-teal-600 hover:bg-teal-700 shadow-teal-500/20 hover:shadow-teal-500/30"
      onSubmit={handleSubmit}
      loading={loading}
      error={error}
    />
  );
}
