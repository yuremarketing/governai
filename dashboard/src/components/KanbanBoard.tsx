'use client';

import { useEffect, useState } from 'react';
import { ParsedTask } from '@/app/api/tasks/route';
import { AlertCircle, CheckCircle2, Clock, PlayCircle } from 'lucide-react';

export default function KanbanBoard() {
  const [tasks, setTasks] = useState<ParsedTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/tasks')
      .then(res => {
        if (!res.ok) throw new Error('Falha ao buscar tarefas');
        return res.json();
      })
      .then(data => {
        setTasks(data.tasks);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center h-64 text-slate-400">Carregando Kanban...</div>;
  }

  if (error) {
    return <div className="p-4 bg-rose-500/10 border border-rose-500/50 text-rose-500 rounded-lg">{error}</div>;
  }

  const columns = [
    { id: 'todo', title: 'A Fazer (Backlog)', icon: Clock, color: 'text-slate-400', border: 'border-slate-800' },
    { id: 'in_progress', title: 'Em Progresso', icon: PlayCircle, color: 'text-cyan-400', border: 'border-cyan-900' },
    { id: 'blocked', title: 'Bloqueadas', icon: AlertCircle, color: 'text-rose-500', border: 'border-rose-900' },
    { id: 'done', title: 'Concluídas', icon: CheckCircle2, color: 'text-emerald-500', border: 'border-emerald-900' }
  ];

  return (
    <div className="flex gap-6 overflow-x-auto pb-4 h-full">
      {columns.map(col => {
        const colTasks = tasks.filter(t => t.status === col.id);
        
        return (
          <div key={col.id} className="flex-shrink-0 w-80 flex flex-col bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
            <div className={`p-4 border-b ${col.border} bg-slate-900 flex justify-between items-center`}>
              <div className="flex items-center gap-2">
                <col.icon size={18} className={col.color} />
                <h3 className="font-semibold text-slate-200">{col.title}</h3>
              </div>
              <span className="bg-slate-800 text-slate-300 text-xs font-bold px-2 py-1 rounded-full">
                {colTasks.length}
              </span>
            </div>
            
            <div className="flex-1 p-4 overflow-y-auto space-y-4">
              {colTasks.length === 0 ? (
                <div className="text-center text-slate-500 text-sm py-8 border border-dashed border-slate-700 rounded-lg">
                  Nenhuma tarefa
                </div>
              ) : (
                colTasks.map(task => (
                  <div key={task.id} className="bg-slate-800 border border-slate-700 p-4 rounded-lg shadow-sm hover:border-slate-600 transition-colors cursor-pointer group">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-xs font-medium text-slate-400 bg-slate-900 px-2 py-1 rounded">
                        {task.id}
                      </span>
                    </div>
                    <h4 className="text-sm text-slate-200 font-medium leading-snug group-hover:text-cyan-300 transition-colors">
                      {task.title}
                    </h4>
                    <div className="mt-3 text-xs text-slate-500 truncate" title={task.category}>
                      {task.category}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
