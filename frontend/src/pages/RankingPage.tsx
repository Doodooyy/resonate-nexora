import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Search, ChevronDown, ChevronRight, User as UserIcon, AlertTriangle, MessageSquare } from 'lucide-react';
import api from '../api';

export default function RankingPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState<any>(null);
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedApp, setSelectedApp] = useState<any>(null);
  const [biasFlags, setBiasFlags] = useState<any[]>([]);
  
  // Chat state
  const [chatOpen, setChatOpen] = useState(false);
  const [compareWith, setCompareWith] = useState<string>('');
  const [chatResponse, setChatResponse] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    fetchJob();
  }, [id]);

  const fetchJob = async () => {
    try {
      const res = await api.get(`/jobs/${id}`);
      setJob(res.data);
      // Fetch bias flags
      const biasRes = await api.get(`/jobs/${id}/bias`);
      setBiasFlags(biasRes.data.flags);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRank = async () => {
    setLoading(true);
    setApplications([]);
    try {
      const res = await api.post(`/jobs/${id}/rank`);
      setApplications(res.data.applications);
    } catch (err) {
      console.error(err);
      alert('Error running ranking engine');
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async () => {
    if (!compareWith || !selectedApp) return;
    
    const targetApp = applications.find(a => a.candidate.name.toLowerCase().includes(compareWith.toLowerCase()) || a.candidate.id.toString() === compareWith);
    if (!targetApp) {
      setChatResponse("Candidate not found for comparison.");
      return;
    }
    
    setChatLoading(true);
    try {
      const res = await api.post(`/jobs/${id}/compare?cand_a_id=${selectedApp.candidate_id}&cand_b_id=${targetApp.candidate_id}`);
      setChatResponse(res.data.explanation);
    } catch (err) {
      setChatResponse("Failed to generate comparison.");
    } finally {
      setChatLoading(false);
    }
  };

  if (!job) return <div className="p-8">Loading job...</div>;

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--color-bg-base)] text-left">
      {/* Sidebar: Job Info & Candidate List */}
      <div className="w-1/3 border-r border-gray-200 bg-white flex flex-col h-full">
        <div className="p-6 border-b border-gray-200">
          <button onClick={() => navigate('/employer')} className="text-xs text-gray-500 mb-4 hover:underline">← Back to Dashboard</button>
          <h1 className="text-2xl font-bold mb-1">{job.title}</h1>
          <p className="text-sm text-gray-500 mb-4">{job.company}</p>
          
          {biasFlags.length > 0 && (
            <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded text-xs text-orange-800">
              <div className="flex items-center font-bold mb-1"><AlertTriangle size={14} className="mr-1"/> JD Bias Warnings ({biasFlags.length})</div>
              {biasFlags.map((flag, idx) => (
                <div key={idx} className="mb-1">• "{flag.phrase}" - {flag.suggestion}</div>
              ))}
            </div>
          )}
          
          <button 
            onClick={handleRank}
            disabled={loading}
            className="w-full bg-[var(--color-primary)] text-white py-2 rounded font-medium hover:bg-opacity-90 transition disabled:opacity-70 flex justify-center items-center"
          >
            {loading ? 'Running AI Shortlisting...' : 'Run Nexora Ranking'}
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4">
          {applications.length > 0 ? (
            <div className="space-y-2">
              <div className="text-xs font-semibold text-gray-500 uppercase mb-2 px-2">Ranked Candidates ({applications.length})</div>
              {applications.map((app, idx) => (
                <div 
                  key={app.id} 
                  onClick={() => { setSelectedApp(app); setChatOpen(false); setChatResponse(''); }}
                  className={`p-3 rounded-lg border cursor-pointer transition flex items-center justify-between ${selectedApp?.id === app.id ? 'bg-purple-50 border-purple-200' : 'bg-white border-gray-100 hover:border-gray-300'}`}
                >
                  <div className="flex items-center">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mr-3 ${app.status === 'shortlisted' ? 'bg-[var(--color-primary)] text-white' : 'bg-gray-200 text-gray-600'}`}>
                      {app.rank}
                    </div>
                    <div>
                      <div className="font-medium text-sm">{app.candidate.name}</div>
                      <div className="text-xs text-gray-500">Score: {app.final_score.toFixed(1)}</div>
                    </div>
                  </div>
                  <ChevronRight size={16} className="text-gray-400" />
                </div>
              ))}
            </div>
          ) : (
             !loading && <div className="text-center text-gray-400 text-sm mt-10">Click Rank to view candidates</div>
          )}
        </div>
      </div>
      
      {/* Main Content: Candidate Details */}
      <div className="flex-1 bg-gray-50 overflow-y-auto">
        {selectedApp ? (
          <div className="p-8 max-w-4xl mx-auto">
            <div className="flex justify-between items-start mb-6">
              <div>
                <div className="flex items-center mb-1">
                  <h2 className="text-3xl font-bold mr-3">{selectedApp.candidate.name}</h2>
                  {selectedApp.status === 'shortlisted' && (
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full">SHORTLISTED</span>
                  )}
                </div>
                <div className="text-gray-500">{selectedApp.candidate.email}</div>
              </div>
              <div className="text-right">
                <div className="text-4xl font-black text-[var(--color-primary)]">{selectedApp.final_score.toFixed(1)}</div>
                <div className="text-xs text-gray-500 font-medium uppercase tracking-wide">Overall Fit Score</div>
              </div>
            </div>
            
            {/* AI Explanation */}
            {selectedApp.explanation && (
              <div className="bg-white p-5 rounded-xl border border-purple-100 shadow-sm mb-6 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-[var(--color-primary)]"></div>
                <h3 className="text-xs font-bold text-gray-400 uppercase mb-2 tracking-wider">Why they ranked #{selectedApp.rank}</h3>
                <p className="text-gray-700 text-sm leading-relaxed">{selectedApp.explanation}</p>
              </div>
            )}
            
            {/* Score Breakdown */}
            <h3 className="text-lg font-bold mb-3 mt-8">Score Breakdown</h3>
            <div className="grid grid-cols-2 gap-4 mb-8">
               <ScoreCard title="Semantic Match" score={selectedApp.semantic_score} desc="Contextual alignment with JD" />
               <ScoreCard title="Keyword Match" score={selectedApp.keyword_score} desc="Explicit skill mentions" />
               <ScoreCard title="Required Skills" score={selectedApp.required_skill_score} desc="Coverage of must-haves" />
               <ScoreCard title="Evidence Coherence" score={selectedApp.coherence_score} desc="Skills backed by projects/exp" />
            </div>
            
            {/* Skills Details */}
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-white p-5 border rounded-lg">
                <h3 className="font-bold text-sm mb-3 uppercase text-gray-500 tracking-wide">Matched Skills</h3>
                <div className="space-y-2">
                  {selectedApp.skill_matches.filter((m: any) => m.matched).map((m: any, i: number) => (
                    <div key={i} className="text-sm flex items-center">
                      <span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>
                      <span className="font-medium">{m.skill}</span>
                      {m.required && <span className="ml-2 text-[10px] bg-gray-100 px-1 rounded text-gray-500">REQ</span>}
                    </div>
                  ))}
                  {selectedApp.skill_matches.filter((m: any) => m.matched).length === 0 && <span className="text-sm text-gray-400">None found</span>}
                </div>
              </div>
              
              <div className="bg-white p-5 border rounded-lg">
                <h3 className="font-bold text-sm mb-3 uppercase text-gray-500 tracking-wide">Missing Required Skills</h3>
                <div className="space-y-2">
                  {selectedApp.skill_matches.filter((m: any) => m.required && !m.matched).map((m: any, i: number) => (
                    <div key={i} className="text-sm flex items-center">
                      <span className="w-2 h-2 rounded-full bg-red-400 mr-2"></span>
                      <span className="font-medium text-gray-600">{m.skill}</span>
                    </div>
                  ))}
                  {selectedApp.skill_matches.filter((m: any) => m.required && !m.matched).length === 0 && <span className="text-sm text-gray-400">All required skills met</span>}
                </div>
              </div>
            </div>
            
            {/* Evidence */}
            <h3 className="text-lg font-bold mb-3 mt-8">Supporting Evidence</h3>
            <div className="space-y-3 mb-10">
              {selectedApp.skill_matches.filter((m: any) => m.matched && m.evidence).map((m: any, i: number) => (
                <div key={i} className="bg-white p-4 border border-gray-200 rounded-lg shadow-sm">
                  <div className="font-bold text-sm mb-1">{m.skill}</div>
                  <div className="text-sm text-gray-600 font-mono text-xs bg-gray-50 p-2 rounded">{m.evidence}</div>
                </div>
              ))}
            </div>
            
            {/* Recruiter Q&A */}
            <div className="fixed bottom-6 right-6">
               {!chatOpen ? (
                 <button onClick={() => setChatOpen(true)} className="bg-black text-white p-4 rounded-full shadow-lg hover:scale-105 transition">
                   <MessageSquare size={24} />
                 </button>
               ) : (
                 <div className="bg-white rounded-lg shadow-xl border w-80 overflow-hidden flex flex-col">
                   <div className="bg-gray-900 text-white p-3 flex justify-between items-center">
                     <span className="font-bold text-sm">Recruiter Q&A</span>
                     <button onClick={() => setChatOpen(false)} className="text-gray-400 hover:text-white">✕</button>
                   </div>
                   <div className="p-4 flex-1">
                     <div className="text-xs text-gray-500 mb-2">Why did {selectedApp.candidate.name} rank above:</div>
                     <input 
                       value={compareWith} 
                       onChange={e => setCompareWith(e.target.value)} 
                       placeholder="Candidate Name..." 
                       className="w-full border p-2 text-sm rounded mb-2"
                     />
                     <button 
                       onClick={handleCompare}
                       disabled={chatLoading || !compareWith}
                       className="w-full bg-[var(--color-primary)] text-white text-sm py-2 rounded disabled:opacity-50"
                     >
                       {chatLoading ? 'Analyzing...' : 'Ask AI'}
                     </button>
                     
                     {chatResponse && (
                       <div className="mt-4 p-3 bg-gray-50 rounded text-sm text-gray-700 border">
                         {chatResponse}
                       </div>
                     )}
                   </div>
                 </div>
               )}
            </div>
            
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            Select a candidate from the ranking list to view details
          </div>
        )}
      </div>
    </div>
  );
}

function ScoreCard({ title, score, desc }: { title: string, score: number, desc: string }) {
  return (
    <div className="bg-white p-4 rounded-lg border border-gray-200">
      <div className="flex justify-between items-center mb-1">
        <div className="font-bold text-sm text-gray-700">{title}</div>
        <div className="font-bold text-lg">{score.toFixed(0)}</div>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-1.5 mb-2">
        <div className="bg-[var(--color-primary)] h-1.5 rounded-full" style={{ width: `${score}%` }}></div>
      </div>
      <div className="text-xs text-gray-400">{desc}</div>
    </div>
  );
}
