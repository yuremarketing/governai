export default function Home() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-white">Visão Geral</h1>
        <p className="text-slate-400 mt-2">Acompanhe as métricas globais e o status dos agentes de IA.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Metric Cards */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-400">Total de Chamadas (LLM)</h3>
          <p className="text-3xl font-bold text-white mt-2">1,204</p>
          <span className="text-xs text-green-400 mt-2 block">+12% desde ontem</span>
        </div>
        
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-400">Tarefas Concluídas</h3>
          <p className="text-3xl font-bold text-white mt-2">48</p>
          <span className="text-xs text-slate-500 mt-2 block">Nesta semana</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm relative overflow-hidden">
          <h3 className="text-sm font-medium text-slate-400">Alertas de Segurança</h3>
          <p className="text-3xl font-bold text-rose-500 mt-2">2</p>
          <span className="text-xs text-rose-400 mt-2 block flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
            Atenção requerida
          </span>
          <div className="absolute top-0 right-0 p-4 opacity-10">
            {/* Background Icon */}
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-rose-500"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
          </div>
        </div>
      </div>

      {/* Recent Activity Mock */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl p-6 mt-8">
        <h2 className="text-xl font-semibold text-white mb-4">Atividade Recente</h2>
        <div className="space-y-4">
          {[
            { task: "TASK-WEB-001", status: "Em progresso", time: "Agora" },
            { task: "TASK-TEST-UX", status: "Concluído", time: "Há 1 hora" },
            { task: "TASK-GOV-TEMP-TEST", status: "Concluído", time: "Há 1 hora" },
          ].map((item, i) => (
            <div key={i} className="flex items-center justify-between py-3 border-b border-slate-800 last:border-0 last:pb-0">
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${item.status === 'Concluído' ? 'bg-green-500' : 'bg-cyan-500'}`}></div>
                <span className="font-medium text-slate-300">{item.task}</span>
              </div>
              <div className="flex gap-4 text-sm">
                <span className={item.status === 'Concluído' ? 'text-green-400' : 'text-cyan-400'}>{item.status}</span>
                <span className="text-slate-500">{item.time}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
