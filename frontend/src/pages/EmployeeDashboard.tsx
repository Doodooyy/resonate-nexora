import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function EmployeeDashboard() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState<any | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    api.get('/jobs').then(res => setJobs(res.data)).catch(console.error);
  }, []);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !selectedJob) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('resume', file);

    try {
      await api.post(`/jobs/${selectedJob.id}/apply`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert('Application submitted successfully!');
      setSelectedJob(null);
      setFile(null);
    } catch (err) {
      alert('Error submitting application');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8 text-left">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Candidate Portal</h1>
        <button onClick={() => navigate('/')} className="text-sm text-gray-500 hover:underline">Logout</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Available Roles</h2>
          <div className="space-y-4">
            {jobs.map(job => (
              <div 
                key={job.id} 
                className={`p-4 border rounded-lg cursor-pointer transition ${selectedJob?.id === job.id ? 'border-[var(--color-primary)] ring-1 ring-[var(--color-primary)]' : 'border-gray-200 hover:border-gray-300'}`}
                onClick={() => setSelectedJob(job)}
              >
                <h3 className="font-medium text-gray-900">{job.title}</h3>
                <p className="text-sm text-gray-500">{job.company}</p>
              </div>
            ))}
          </div>
        </div>

        <div>
          {selectedJob ? (
            <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <h2 className="text-xl font-bold mb-2">Apply for {selectedJob.title}</h2>
              <div className="prose prose-sm mb-6 max-h-64 overflow-y-auto bg-gray-50 p-4 rounded text-xs whitespace-pre-wrap">
                {selectedJob.description}
              </div>

              <form onSubmit={handleApply}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Upload Resume (PDF)</label>
                  <input 
                    type="file" 
                    accept=".pdf"
                    required
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-[var(--color-primary-bg)] file:text-[var(--color-primary)] hover:file:bg-purple-100"
                  />
                </div>
                <button 
                  type="submit" 
                  disabled={!file || uploading}
                  className="w-full bg-[var(--color-primary)] text-white px-4 py-2 rounded font-medium disabled:opacity-50 hover:bg-opacity-90"
                >
                  {uploading ? 'Submitting...' : 'Submit Application'}
                </button>
              </form>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full min-h-[300px] border border-dashed border-gray-300 rounded-lg bg-gray-50 text-gray-400">
              Select a job to view details and apply
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
