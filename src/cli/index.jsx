// src/cli/index.js
import { Command } from 'commander';
import { getAllChats } from '../core/chatApi.jsx';

const program = new Command();

program
  .name('jarvis')
  .description('CLI para interactuar con el RAG Crítico')
  .version('1.0.0');

program
  .command('list')
  .description('Listar todos los chats del usuario')
  .action(async () => {
    try {
      const chats = await getAllChats();
      console.table(chats.map(c => ({ id: c.id, titulo: c.title })));
    } catch (error) {
      console.error("Error al conectar con el backend:", error.message);
    }
  });

program.parse();