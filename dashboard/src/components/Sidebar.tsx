import Link from "next/link";
import { LayoutDashboard, Kanban, ShieldAlert, Settings } from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="w-64 h-screen bg-slate-900 border-r border-slate-800 flex flex-col fixed left-0 top-0">
      <div className="p-6">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <span className="text-cyan-400">Govern</span>AI
        </h1>
      </div>
      <nav className="flex-1 px-4 space-y-2 mt-4">
        <Link href="/" className="flex items-center gap-3 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
          <LayoutDashboard size={20} />
          <span>Visão Geral</span>
        </Link>
        <Link href="/kanban" className="flex items-center gap-3 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
          <Kanban size={20} />
          <span>Kanban (Tarefas)</span>
        </Link>
        <Link href="/audit" className="flex items-center gap-3 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
          <ShieldAlert size={20} />
          <span>Auditoria e Logs</span>
        </Link>
        <Link href="/settings" className="flex items-center gap-3 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
          <Settings size={20} />
          <span>Configurações</span>
        </Link>
      </nav>
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
        GovernAI Dashboard v1.0
      </div>
    </aside>
  );
}
