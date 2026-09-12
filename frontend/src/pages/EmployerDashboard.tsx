import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Plus } from 'lucide-react';

export default function EmployerDashboard() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    description: '',
    location: '',
    years_of_experience: 0,
    qualification: '',
    required_skills: '',
    preferred_skills: '',
    responsibilities: '',
    shortlist_size: 5
  });

  const fetchJobs = () => {
    api.get('/jobs').then(res => setJobs(res.data)).catch(console.error);
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Convert comma separated strings to arrays
    const splitClean = (str: string) => str.split(',').map(s => s.trim()).filter(s => s.length > 0);
    
    const payload = {
      title: formData.title,
      company: formData.company,
      description: formData.description,
      location: formData.location,
      years_of_experience: Number(formData.years_of_experience),
      qualification: formData.qualification,
      required_skills: splitClean(formData.required_skills),
      preferred_skills: splitClean(formData.preferred_skills),
      responsibilities: splitClean(formData.responsibilities),
      shortlist_size: formData.shortlist_size
    };
    
    try {
      await api.post('/jobs/', payload);
      setShowForm(false);
      setFormData({
        title: '', company: '', description: '', location: '', years_of_experience: 0, qualification: '',
        required_skills: '', preferred_skills: '', responsibilities: '', shortlist_size: 5
      });
      fetchJobs();
    } catch (err) {
      console.error(err);
      alert('Error creating job');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="max-w-4xl mx-auto p-8 text-left">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Employer Dashboard</h1>
        <button onClick={() => navigate('/')} className="text-sm text-gray-500 hover:underline">Logout</button>
      </div>

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Your Posted Jobs</h2>
        <button 
          onClick={() => setShowForm(!showForm)}
          className="flex items-center text-sm font-medium bg-[var(--color-primary)] text-white px-4 py-2 rounded shadow-sm hover:bg-opacity-90"
        >
          <Plus size={16} className="mr-1" />
          Create New Job
        </button>
      </div>
      
      {showForm && (
        <div className="bg-white p-6 border rounded-lg shadow-sm mb-8">
          <h3 className="text-lg font-bold mb-4">Create New Job Description</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Job Title</label>
                <input required name="title" value={formData.title} onChange={handleChange} className="w-full border rounded p-2 text-sm" placeholder="e.g. Full Stack Developer" />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Company</label>
                <input required name="company" value={formData.company} onChange={handleChange} className="w-full border rounded p-2 text-sm" placeholder="e.g. TechCorp" />
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Location</label>
                <input required name="location" value={formData.location} onChange={handleChange} className="w-full border rounded p-2 text-sm" placeholder="e.g. New York, NY or Remote" />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Years of Experience</label>
                <input required type="number" min="0" name="years_of_experience" value={formData.years_of_experience} onChange={handleChange} className="w-full border rounded p-2 text-sm" />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Required Qualification</label>
                <input required name="qualification" value={formData.qualification} onChange={handleChange} className="w-full border rounded p-2 text-sm" placeholder="e.g. Bachelor's in CS" />
              </div>
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Full Description / JD Text</label>
              <textarea required name="description" value={formData.description} onChange={handleChange} rows={5} className="w-full border rounded p-2 text-sm" placeholder="Paste the full job description here..."></textarea>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Required Skills (Comma separated)</label>
                <input required name="required_skills" value={formData.required_skills} onChange={handleChange} className="w-full border rounded p-2 text-sm" placeholder="e.g. React, Node.js, REST APIs" />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Preferred Skills (Comma separated)</label>
                <input name="preferred_skills" value={formData.preferred_skills} onChange={handleChange} className="w-full border rounded p-2 text-sm" placeholder="e.g. AWS, Docker" />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Responsibilities (Comma separated)</label>
                <input name="responsibilities" value={formData.responsibilities} onChange={handleChange} className="w-full border rounded p-2 text-sm" placeholder="e.g. Build backend, Design UI" />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Shortlist Size</label>
                <input type="number" min="1" max="50" name="shortlist_size" value={formData.shortlist_size} onChange={handleChange} className="w-full border rounded p-2 text-sm" />
              </div>
            </div>
            
            <div className="flex justify-end space-x-2 pt-2">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm border rounded text-gray-600 hover:bg-gray-50">Cancel</button>
              <button type="submit" className="px-4 py-2 text-sm bg-black text-white rounded font-medium hover:bg-gray-800">Publish Job</button>
            </div>
          </form>
        </div>
      )}
      
      <div className="space-y-4">
        {jobs.map(job => (
          <div key={job.id} className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition">
            <h3 className="text-lg font-bold">{job.title}</h3>
            <p className="text-sm text-gray-500 mb-4">{job.company}</p>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
                Target Shortlist Size: {job.shortlist_size}
              </span>
              <button 
                onClick={() => navigate(`/employer/jobs/${job.id}`)}
                className="bg-black text-white px-4 py-2 rounded text-sm font-medium hover:bg-gray-800 transition"
              >
                View Candidates
              </button>
            </div>
          </div>
        ))}
        {jobs.length === 0 && <p className="text-gray-500">No jobs posted yet.</p>}
      </div>
    </div>
  );
}
