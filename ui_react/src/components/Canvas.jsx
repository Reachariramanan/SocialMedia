import React from 'react'
import LeftPane from './LeftPane'
import SignalStream from './lenses/SignalStream'

export default function Canvas({
  mode, setMode,
  snapshot, snapshotLoading,
  runs, selectedRun, html, runHistory, onSelectRun, runsLoading,
  agentRun,
  discover,
  feeds,
  systemStatus,
  onTagClick,
  activeQuery,
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
        runsLoading={runsLoading}
        agentRun={agentRun}
        discover={discover}
        feeds={feeds}
        activeQuery={activeQuery}
      />
      <SignalStream
        snapshot={snapshot}
        loading={snapshotLoading}
        onTagClick={onTagClick}
      />
    </div>
  )
}
