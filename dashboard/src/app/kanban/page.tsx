import KanbanBoard from "@/components/KanbanBoard";

export default function KanbanPage() {
  return (
    <div className="h-full flex flex-col">
      <header className="mb-6">
        <h1 className="text-3xl font-bold text-white">Kanban (Tarefas)</h1>
        <p className="text-slate-400 mt-2">Visão em tempo real das tarefas sincronizadas com o arquivo TASKS.md.</p>
      </header>
      
      <div className="flex-1 min-h-0">
        <KanbanBoard />
      </div>
    </div>
  );
}
