import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { GraduationCap } from 'lucide-react';
import { LoginPage as SharedLoginPage } from 'school-erp-ui-shared';
import { login, clearError } from '../../store/authSlice';

export default function LoginPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((s) => s.auth);

  const handleSubmit = async (data) => {
    dispatch(clearError());
    const result = await dispatch(login(data));
    if (result.meta.requestStatus === 'fulfilled') {
      navigate('/admin/dashboard');
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
