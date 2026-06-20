import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export interface ParsedTask {
  id: string;
  title: string;
  status: 'todo' | 'in_progress' | 'done' | 'blocked';
  category: string;
}

export async function GET() {
  try {
    // Acessa o arquivo TASKS.md que está um diretório acima do dashboard
    const tasksFilePath = path.join(process.cwd(), '..', 'TASKS.md');
    
    if (!fs.existsSync(tasksFilePath)) {
      return NextResponse.json({ error: 'Arquivo TASKS.md não encontrado' }, { status: 404 });
    }

    const content = fs.readFileSync(tasksFilePath, 'utf-8');
    const tasks: ParsedTask[] = [];
    
    let currentCategory = 'General';
    const lines = content.split('\n');
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Identifica categoria (ex: ## 🛡️ Segurança & Privacidade)
      if (line.startsWith('## ') && !line.includes('TASKS — GovernAI') && !line.includes('Concluídas')) {
        currentCategory = line.replace('## ', '').trim();
      }
      
      // Identifica Tarefa (ex: ### TASK-001 — Titulo)
      if (line.startsWith('### TASK-')) {
        const titleMatch = line.match(/###\s+(TASK-[A-Z0-9-]+)\s*[-—]\s*(.+)/);
        if (titleMatch) {
          const id = titleMatch[1];
          const title = titleMatch[2].trim();
          
          // Busca o status nas próximas linhas
          let status: ParsedTask['status'] = 'todo';
          for (let j = i + 1; j < Math.min(i + 10, lines.length); j++) {
            const statusLine = lines[j].trim();
            if (statusLine.startsWith('**Status:**')) {
              if (statusLine.includes('[x]')) status = 'done';
              else if (statusLine.includes('[/]')) status = 'in_progress';
              else if (statusLine.includes('❌') || statusLine.toLowerCase().includes('bloqueada')) status = 'blocked';
              else status = 'todo';
              break;
            }
            if (statusLine.startsWith('---')) break;
          }
          
          tasks.push({ id, title, status, category: currentCategory });
        }
      }
    }
    
    return NextResponse.json({ tasks });
  } catch (error) {
    console.error('Error reading TASKS.md:', error);
    return NextResponse.json({ error: 'Erro interno ao processar TASKS.md' }, { status: 500 });
  }
}
