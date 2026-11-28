// progresso — a porcentagem de tarefas declaradas, numa faixa acima do campo de digitação.
//
// Por que existe: numa sessão longa dá para trabalhar horas sem o outro lado saber em que pé está.
// A honestidade deste mod tem dois lados:
//
//   1. A porcentagem é SOBRE AS TAREFAS DECLARADAS, não sobre "quanto falta do trabalho". Essa
//      segunda não é mensurável: trabalho aparece no meio do caminho. Então quando o total cresce,
//      a barra ANDA PARA TRÁS, de propósito. Uma barra que cai de 60% para 40% porque apareceu
//      mais trabalho é mais útil que uma que mente para parecer que avança.
//   2. Quando não há tarefa declarada nenhuma, ele diz isso. É a informação mais importante que
//      ele dá: significa que ninguém está acompanhando nada.
import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Contagem } from '../types'

const VAZIO: Contagem = { total: 0, prontas: 0, emCurso: null }

const contagem = atom({ plugin: 'progresso', key: 'contagem' } as const, VAZIO)

const LARGURA = 10

// o assunto da tarefa em curso, cortado para a faixa não empurrar o resto da linha
function corta(assunto: string): string {
  return assunto.length > 38 ? assunto.slice(0, 37) + '…' : assunto
}

export const register: Register = on => {
  // TaskList é a fonte autoritativa: recontagem completa, e conserta qualquer deriva.
  on('tool.call', { tool: 'TaskList' }, async ($, e, next) => {
    const r = await next(e)
    const tarefas = !r.isError ? r.result?.tasks : undefined
    if (tarefas) {
      const emCurso = tarefas.find(t => t.status === 'in_progress')
      await update($, contagem, () => ({
        total: tarefas.length,
        prontas: tarefas.filter(t => t.status === 'completed').length,
        emCurso: emCurso ? emCurso.subject : null,
      }))
    }
    return r
  })

  // Tarefa nova: o total cresce. É aqui que a barra pode andar para trás, e é certo que ande.
  on('tool.call', { tool: 'TaskCreate' }, async ($, e, next) => {
    const r = await next(e)
    if (!r.isError && r.result?.task) {
      await update($, contagem, c => ({ ...c, total: c.total + 1 }))
    }
    return r
  })

  // O resultado do TaskUpdate traz statusChange { from, to } — vem do motor, não é inferência.
  on('tool.call', { tool: 'TaskUpdate' }, async ($, e, next) => {
    const r = await next(e)
    const mudou = !r.isError ? r.result?.statusChange : undefined
    if (mudou) {
      const { from, to } = mudou
      const assunto = e.activeForm ?? e.subject ?? null
      await update($, contagem, c => {
        const prontas = c.prontas + (to === 'completed' ? 1 : 0) - (from === 'completed' ? 1 : 0)
        let emCurso = c.emCurso
        if (to === 'in_progress') emCurso = assunto ?? emCurso
        else if (from === 'in_progress') emCurso = null
        return { total: c.total, prontas: Math.max(0, prontas), emCurso }
      })
    }
    return r
  })

  // A faixa, acima do campo de digitação. Escrever no atom (update) redesenha quem o lê, então
  // não há nada a empurrar: os hooks acima só contam, e esta função desenha.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    // Numa pesquisa do próprio app, a faixa sai da frente.
    if (e.props.hasSurvey) return next(e)

    const c = await read($, contagem)
    const { Box, Text } = $.ui.resolve(e)

    if (c.total === 0) {
      return (
        <Box>
          <Text dimColor>○ nenhuma tarefa declarada</Text>
        </Box>
      )
    }

    const fracao = c.prontas / c.total
    const cheias = Math.round(fracao * LARGURA)
    const pct = Math.round(fracao * 100)

    return (
      <Box>
        <Text color={pct === 100 ? 'green' : 'cyan'}>
          {'▓'.repeat(cheias)}
          <Text dimColor>{'░'.repeat(LARGURA - cheias)}</Text>
        </Text>
        <Text>{` ${c.prontas}/${c.total} · ${pct}%`}</Text>
        {c.emCurso ? <Text dimColor>{` · ${corta(c.emCurso)}`}</Text> : null}
      </Box>
    )
  })
}
