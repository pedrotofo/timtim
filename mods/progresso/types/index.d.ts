export type Contagem = {
  /** Tarefas declaradas. Cresce quando apareceu trabalho que não estava previsto. */
  total: number
  /** Tarefas concluídas. */
  prontas: number
  /** Assunto da tarefa em curso, para a linha dizer o que está acontecendo. */
  emCurso: string | null
}

declare module 'claude-code' {
  interface PluginState {
    progresso: { contagem: Contagem }
  }
}
