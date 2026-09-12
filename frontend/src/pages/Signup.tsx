import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

export default function Signup() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('employer');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.post('/auth/signup', {
        email,
        password,
        role
      });
      
      // Auto login after signup
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const res = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify(res.data.user));

      if (role === 'employer') {
        navigate('/employer');
      } else {
        navigate('/employee');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during signup');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <div className="w-full max-w-md p-8 bg-white shadow rounded-lg border border-gray-200 text-left">
        <h1 className="text-3xl font-bold mb-2 text-center">NEXORA</h1>
        <p className="text-center text-gray-500 mb-8">Create your account</p>
        
        {error && <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded border border-red-200">{error}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">I am a...</label>
            <div className="flex space-x-4">
              <label className="flex items-center text-sm cursor-pointer">
                <input type="radio" value="employer" checked={role === 'employer'} onChange={e => setRole(e.target.value)} className="mr-2" />
                Recruiter / Employer
              </label>
              <label className="flex items-center text-sm cursor-pointer">
                <input type="radio" value="employee" checked={role === 'employee'} onChange={e => setRole(e.target.value)} className="mr-2" />
                Candidate
              </label>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input 
              type="email" 
              required 
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full border rounded p-2 text-sm" 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input 
              type="password" 
              required 
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full border rounded p-2 text-sm" 
              minLength={6}
            />
          </div>
          
          <button 
            type="submit" 
            disabled={loading}
            className="w-full py-3 px-4 bg-black text-white font-medium rounded shadow hover:bg-gray-800 transition mt-4 disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm text-gray-500">
          Already have an account? <Link to="/" className="text-[var(--color-primary)] hover:underline font-medium">Log in</Link>
        </div>
      </div>
    </div>
  );
}
