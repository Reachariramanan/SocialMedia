import React from 'react'
import LeftPane from './LeftPane'
import SignalStream from './lenses/SignalStream'

export default function Canvas({
  mode, setMode,
  snapshot, snapshotLoading,
  runs, selectedRun, html, runHistory, onSelectRun, onDeleteRun, reloadRuns, runsLoading,
  agentRun,
  activeSkill,
  discover,
  feeds,
  xtraction,
  systemStatus,
  onTagClick,
  activeQuery,
  schedules,
}) {
  return (
    <div className="canvas">
      <LeftPane
        mode={mode}
        setMode={setMode}
        runs={runs}
        selectedRun={selectedRun}
        html={html}
        runHistory={runHistory}
        onSelectRun={onSelectRun}
        onDeleteRun={onDeleteRun}
        reloadRuns={reloadRuns}
        runsLoading={runsLoading}
        agentRun={agentRun}
        activeSkill={activeSkill}
        discover={discover}
        feeds={feeds}
        xtraction={xtraction}
        activeQuery={activeQuery}
        schedules={schedules}
      />
      <SignalStream
        snapshot={snapshot}
        loading={snapshotLoading}
        onTagClick={onTagClick}
      />
    </div>
  )
}
