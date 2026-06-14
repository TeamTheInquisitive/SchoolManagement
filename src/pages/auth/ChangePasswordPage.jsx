import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ChangePassword } from 'school-erp-ui-shared';

function AdminChangePasswordPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleChangePassword = async (passwords) => {
    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // Get token from localStorage or your auth service
      const token = localStorage.getItem('authToken');

      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:3001'}/api/admin/change-password`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            currentPassword: passwords.currentPassword,
            newPassword: passwords.newPassword,
          }),
          credentials: 'include',
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Failed to change password');
      }

      // Success!
      setSuccessMessage('Password changed successfully! Redirecting...');

      // Navigate back after 2 seconds to show success message
      setTimeout(() => {
        navigate(location.state?.from || '/admin/dashboard');
      }, 2000);
    } catch (err) {
      console.error('Password change error:', err);
      setError(err.message || 'An error occurred while changing your password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChangePassword
      onSubmit={handleChangePassword}
      isLoading={isLoading}
      error={error}
      successMessage={successMessage}
      returnRoute={location.state?.from || '/admin/dashboard'}
    />
  );
}

export default AdminChangePasswordPage;
